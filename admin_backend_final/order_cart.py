# Standard Library
import json
import uuid
import traceback
from decimal import Decimal

# Django
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Prefetch, Q

# Django REST Framework
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .utilities import generate_custom_order_id
from .models import (
    Cart, CartItem, Product, ProductInventory, Attribute,
    Orders, OrderItem, OrderDelivery, Image
)
from .permissions import FrontendOnlyPermission


class SaveCartAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def _get_primary_cart(self, device_uuid: str) -> Cart:
        cart = (
            Cart.objects
            .filter(device_uuid=device_uuid)
            .only("id", "pk", "cart_id", "device_uuid", "updated_at", "created_at")
            .order_by("-updated_at", "-created_at")
            .first()
        )
        if cart:
            dup_ids = list(
                Cart.objects.filter(device_uuid=device_uuid).exclude(pk=cart.pk).values_list("pk", flat=True)
            )
            if dup_ids:
                CartItem.objects.filter(cart_id__in=dup_ids).update(cart=cart)
                Cart.objects.filter(pk__in=dup_ids).delete()
            return cart
        return Cart.objects.create(cart_id=str(uuid.uuid4()), device_uuid=device_uuid)

    def post(self, request):
        try:
            data = request.data if isinstance(request.data, dict) else json.loads(request.body or "{}")

            device_uuid = data.get("device_uuid") or request.headers.get("X-Device-UUID")
            if not device_uuid:
                return Response({"error": "Missing device UUID."}, status=status.HTTP_400_BAD_REQUEST)

            product_id = data.get("product_id")
            if not product_id:
                return Response({"error": "Missing product_id."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                quantity = int(data.get("quantity", 1))
            except Exception:
                quantity = 1

            selected_size = (data.get("selected_size") or "").strip()
            selected_attributes = data.get("selected_attributes") or {}

            product = get_object_or_404(
                Product.objects.only("id", "product_id", "price", "discounted_price"),
                product_id=product_id
            )
            get_object_or_404(
                ProductInventory.objects.only("id", "product_id"),
                product=product
            )

            cart = self._get_primary_cart(device_uuid)

            # ----- compute attribute delta (batch for provided map) -----
            attrs_delta_sum = Decimal("0.00")
            if isinstance(selected_attributes, dict) and selected_attributes:
                opt_ids = {str(v) for v in selected_attributes.values() if v is not None}
                if opt_ids:
                    opts = Attribute.objects.filter(attr_id__in=opt_ids).only("attr_id", "price_delta")
                    for opt in opts:
                        if opt.price_delta is not None:
                            try:
                                attrs_delta_sum += Decimal(str(opt.price_delta))
                            except Exception:
                                pass

            base_price = Decimal(str(product.discounted_price or product.price or 0))
            unit_price = base_price + attrs_delta_sum

            # deterministic signature (no helper)
            sig_parts = [f"size:{selected_size or ''}"]
            if isinstance(selected_attributes, dict):
                for k, v in sorted(selected_attributes.items(), key=lambda x: x[0]):
                    sig_parts.append(f"{k}:{v}")
            variant_signature = "|".join(sig_parts)

            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                variant_signature=variant_signature,
                defaults={
                    "item_id": str(uuid.uuid4()),
                    "quantity": quantity,
                    "price_per_unit": unit_price,
                    "subtotal": unit_price * quantity,
                    "selected_size": selected_size,
                    "selected_attributes": selected_attributes,
                    "attributes_price_delta": attrs_delta_sum,
                }
            )

            if not created:
                cart_item.quantity = cart_item.quantity + quantity
                cart_item.price_per_unit = unit_price
                cart_item.attributes_price_delta = attrs_delta_sum
                cart_item.selected_size = selected_size
                cart_item.selected_attributes = selected_attributes
                cart_item.subtotal = unit_price * cart_item.quantity
                cart_item.save(update_fields=[
                    "quantity", "price_per_unit", "attributes_price_delta",
                    "selected_size", "selected_attributes", "subtotal", "updated_at"
                ])

            return Response({"message": "Cart updated successfully."}, status=status.HTTP_200_OK)

        except Exception as e:
            print("❌ [SAVE_CART] Error:", str(e))
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ShowCartAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def _respond(self, request, device_uuid):
        if not device_uuid:
            return Response({"error": "Missing device UUID."}, status=status.HTTP_400_BAD_REQUEST)

        cart = (
            Cart.objects
            .filter(device_uuid=device_uuid)
            .only("id", "pk", "device_uuid", "updated_at", "created_at")
            .order_by("-updated_at", "-created_at")
            .first()
        )
        if not cart:
            return Response({"cart_items": []}, status=status.HTTP_200_OK)

        items = (
            CartItem.objects
            .filter(cart=cart)
            .select_related("product")
            .only(
                "id", "item_id", "quantity", "price_per_unit", "subtotal",
                "selected_size", "selected_attributes", "attributes_price_delta",
                "variant_signature",
                "product__id", "product__product_id", "product__title", "product__price", "product__discounted_price",
            )
        )

        # ----- batch: preload first image per product -----
        product_ids = [i.product.product_id for i in items]
        img_map = {}
        if product_ids:
            images = (
                Image.objects
                .filter(linked_table="product", linked_id__in=product_ids)
                .only("linked_id", "url", "alt_text", "created_at")
                .order_by("linked_id", "created_at")
            )
            seen = set()
            for im in images:
                if im.linked_id not in seen:
                    img_map[im.linked_id] = im
                    seen.add(im.linked_id)

        # ----- batch: attributes for all items (no helpers) -----
        # collect all parent & option ids present across items
        all_parent_ids = set()
        all_opt_ids = set()
        raw_sel_by_item = {}  # item.pk -> selected_attributes
        for it in items:
            sel = it.selected_attributes or {}
            raw_sel_by_item[it.pk] = sel
            if isinstance(sel, dict):
                for pid, oid in sel.items():
                    if pid is not None:
                        all_parent_ids.add(str(pid))
                    if oid is not None:
                        all_opt_ids.add(str(oid))

        attr_by_id = {}
        if all_parent_ids or all_opt_ids:
            attrs = Attribute.objects.filter(
                Q(attr_id__in=all_parent_ids) | Q(attr_id__in=all_opt_ids)
            ).select_related("parent")
            attr_by_id = {a.attr_id: a for a in attrs}

        response_data = []
        for item in items:
            # humanize selections + sum deltas inline
            selections = []
            attrs_delta = Decimal("0.00")
            sel = raw_sel_by_item.get(item.pk) or {}
            if isinstance(sel, dict):
                for parent_id, opt_id in sel.items():
                    opt = attr_by_id.get(str(opt_id))
                    parent = opt.parent if (opt and opt.parent and opt.parent.attr_id == str(parent_id)) else attr_by_id.get(str(parent_id))
                    price_delta = Decimal("0.00")
                    if opt and opt.price_delta is not None:
                        try:
                            price_delta = Decimal(str(opt.price_delta))
                        except Exception:
                            price_delta = Decimal("0.00")
                    attrs_delta += price_delta
                    selections.append({
                        "attribute_id": str(parent_id),
                        "option_id": str(opt_id),
                        "attribute_name": (parent.name if parent else str(parent_id)),
                        "option_label": (getattr(opt, "label", None) or str(opt_id)),
                        "price_delta": str(price_delta),
                    })

            base_price = Decimal(str(item.product.discounted_price or item.product.price or 0))
            unit_price = base_price + attrs_delta
            line_total = unit_price * item.quantity

            im = img_map.get(item.product.product_id)
            image_url = request.build_absolute_uri(im.url) if (im and getattr(im, "url", None)) else None
            alt_text = getattr(im, "alt_text", "") if im else ""

            # build frontend-required fields
            response_data.append({
                "cart_item_id": item.item_id,                  # 🔑 used by frontend
                "variant_signature": item.variant_signature,    # 🔑 used by frontend
                "product_id": item.product.product_id,
                "product_name": item.product.title,
                "product_image": image_url,
                "alt_text": alt_text,
                "quantity": item.quantity,
                "selected_size": item.selected_size or "",
                "selected_attributes": sel,
                "selected_attributes_human": selections,
                "price_breakdown": {
                    "base_price": str(base_price),
                    "attributes_delta": str(attrs_delta),
                    "unit_price": str(unit_price),
                    "quantity": item.quantity,
                    "line_total": str(line_total),
                },
            })

        return Response({"cart_items": response_data}, status=status.HTTP_200_OK)

    def get(self, request):
        device_uuid = request.headers.get('X-Device-UUID')
        return self._respond(request, device_uuid)

    def post(self, request):
        device_uuid = request.headers.get('X-Device-UUID')
        if not device_uuid:
            try:
                data = request.data if isinstance(request.data, dict) else json.loads(request.body or "{}")
                device_uuid = data.get("device_uuid")
            except Exception:
                device_uuid = None
        return self._respond(request, device_uuid)


class DeleteCartItemAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        try:
            data = request.data if isinstance(request.data, dict) else json.loads(request.body or "{}")
            user_id = data.get('user_id')            # could be user id or device UUID
            product_id = data.get('product_id')
            variant_signature = data.get('variant_signature', "").strip()  # ✅ support precise variant deletion

            if not user_id or not product_id:
                return Response({"error": "user_id and product_id are required."}, status=status.HTTP_400_BAD_REQUEST)

            DjangoUser = get_user_model()
            try:
                user = DjangoUser.objects.get(user_id=user_id)
                cart = Cart.objects.filter(user=user).only("id", "pk").first()
            except DjangoUser.DoesNotExist:
                cart = Cart.objects.filter(device_uuid=user_id).only("id", "pk").first()

            if not cart:
                return Response({"error": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)

            qs = CartItem.objects.filter(cart=cart, product__product_id=product_id)
            if variant_signature:
                qs = qs.filter(variant_signature=variant_signature)

            if not qs.exists():
                return Response({"error": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)

            qs.delete()
            return Response({"message": "Cart item(s) deleted successfully."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SaveOrderAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    @transaction.atomic
    def post(self, request):
        try:
            data = request.data if isinstance(request.data, dict) else json.loads(request.body or "{}")

            user_name = data.get("user_name", "Guest")
            delivery_data = data.get("delivery") or {}
            email = delivery_data.get("email") or None

            order_id = generate_custom_order_id(user_name, email or "")
            order = Orders.objects.create(
                order_id=order_id,
                user_name=user_name,
                order_date=timezone.now(),
                status=data.get("status", "pending"),
                total_price=Decimal(str(data.get("total_price", "0"))),
                notes=data.get("notes", "")
            )

            items = data.get("items") or []
            if not isinstance(items, list) or not items:
                return Response({"error": "No items provided"}, status=status.HTTP_400_BAD_REQUEST)

            # upfront validation + batch product fetch
            product_ids = []
            for item in items:
                for field in ["product_id", "quantity", "unit_price", "total_price"]:
                    if field not in item:
                        return Response({"error": f"Missing {field} in item"}, status=status.HTTP_400_BAD_REQUEST)
                product_ids.append(item["product_id"])

            products = {
                p.product_id: p for p in
                Product.objects.filter(product_id__in=product_ids).only("id", "product_id")
            }
            if len(products) != len(set(product_ids)):
                return Response({"error": "One or more products not found"}, status=status.HTTP_400_BAD_REQUEST)

            new_items = []
            for item in items:
                product = products[item["product_id"]]
                try:
                    qty = int(item.get("quantity", 1))
                except Exception:
                    qty = 1
                unit_price = Decimal(str(item.get("unit_price", "0")))
                total_price = Decimal(str(item.get("total_price", "0")))
                attrs_delta = Decimal(str(item.get("attributes_price_delta", 0)))

                if item.get("base_price") is not None:
                    base_price = Decimal(str(item["base_price"]))
                else:
                    base_price = unit_price - attrs_delta
                    if base_price < 0:
                        base_price = Decimal("0")

                selected_size = (item.get("selected_size") or "").strip()
                selected_attributes = item.get("selected_attributes") or {}
                selected_attributes_human = item.get("selected_attributes_human") or []
                variant_signature = item.get("variant_signature") or ""

                price_breakdown = {
                    "base_price": str(base_price),
                    "attributes_delta": str(attrs_delta),
                    "unit_price": str(unit_price),
                    "line_total": str(total_price),
                    "selected_size": selected_size,
                    "selected_attributes_human": selected_attributes_human,
                }

                new_items.append(OrderItem(
                    item_id=str(uuid.uuid4()),
                    order=order,
                    product=product,
                    quantity=qty,
                    unit_price=unit_price,
                    total_price=total_price,
                    selected_size=selected_size,
                    selected_attributes=selected_attributes,
                    selected_attributes_human=selected_attributes_human,
                    variant_signature=variant_signature,
                    attributes_price_delta=attrs_delta,
                    price_breakdown=price_breakdown,
                ))

            OrderItem.objects.bulk_create(new_items, batch_size=500)

            # normalize delivery instructions to list
            raw_instructions = delivery_data.get("instructions", [])
            if isinstance(raw_instructions, str):
                raw_instructions = [raw_instructions] if raw_instructions.strip() else []
            elif not isinstance(raw_instructions, list):
                raw_instructions = []

            OrderDelivery.objects.create(
                delivery_id=str(uuid.uuid4()),
                order=order,
                name=delivery_data.get("name", user_name),
                email=email,
                phone=delivery_data.get("phone", ""),
                street_address=delivery_data.get("street_address", ""),
                city=delivery_data.get("city", ""),
                zip_code=delivery_data.get("zip_code", ""),
                instructions=raw_instructions,
            )

            return Response({"message": "Order saved successfully", "order_id": order_id}, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(traceback.format_exc())
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ShowOrderAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def get(self, request):
        try:
            orders = (
                Orders.objects
                .all()
                .order_by('-created_at')
                .prefetch_related(
                    Prefetch(
                        'orderitem_set',
                        queryset=OrderItem.objects.select_related('product').only(
                            'id', 'quantity', 'unit_price', 'total_price',
                            'selected_size', 'selected_attributes_human',
                            'variant_signature', 'price_breakdown',
                            'product__id', 'product__product_id', 'product__title'
                        )
                    )
                )
            )

            order_ids = [o.id for o in orders]
            deliveries = {}
            if order_ids:
                for d in OrderDelivery.objects.filter(order_id__in=order_ids).only(
                    'order_id', 'email', 'street_address', 'city', 'zip_code'
                ):
                    deliveries[d.order_id] = d

            orders_data = []
            for order in orders:
                delivery = deliveries.get(order.id)
                address = {}
                email = ""
                if delivery:
                    address = {
                        "street": delivery.street_address,
                        "city": delivery.city,
                        "zip": delivery.zip_code
                    }
                    email = delivery.email or ""

                items_detail = []
                for it in order.orderitem_set.all():
                    human = it.selected_attributes_human or []
                    tokens = []
                    if it.selected_size:
                        tokens.append(f"Size: {it.selected_size}")
                    for d in human:
                        tokens.append(f"{d.get('attribute_name','')}: {d.get('option_label','')}")

                    # math parts (base + deltas)
                    try:
                        base_val = (it.price_breakdown or {}).get("base_price", it.unit_price)
                        base = Decimal(str(base_val))
                    except Exception:
                        base = it.unit_price

                    deltas = []
                    for d in human:
                        try:
                            deltas.append(str(Decimal(str(d.get("price_delta", "0") or "0"))))
                        except Exception:
                            deltas.append("0")

                    items_detail.append({
                        "product_id": it.product.product_id,
                        "product_name": it.product.title,
                        "quantity": it.quantity,
                        "unit_price": str(it.unit_price),
                        "total_price": str(it.total_price),
                        "selection": ", ".join([t for t in tokens if t]),
                        "math": {
                            "base": str(base),
                            "deltas": deltas,
                        },
                        "variant_signature": it.variant_signature or "",
                    })

                orders_data.append({
                    "orderID": order.order_id,
                    "Date": order.order_date.strftime('%Y-%m-%d %H:%M:%S'),
                    "UserName": order.user_name,
                    "item": {
                        "count": len(items_detail),
                        "names": [x["product_name"] for x in items_detail],
                        "detail": items_detail,
                    },
                    "total": float(order.total_price),
                    "status": order.status,
                    "Address": address,
                    "email": email,
                    "order_placed_on": order.created_at.strftime('%Y-%m-%d %H:%M:%S')
                })

            return Response({"orders": orders_data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EditOrderAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    @transaction.atomic
    def put(self, request):
        try:
            data = request.data if isinstance(request.data, dict) else json.loads(request.body or "{}")

            order_id = data.get("order_id")
            if not order_id:
                return Response({"error": "Missing order_id in request body"}, status=status.HTTP_400_BAD_REQUEST)

            order = get_object_or_404(Orders, order_id=order_id)

            order.user_name = data.get("user_name", order.user_name)
            order.status = data.get("status", order.status)
            if data.get("total_price") is not None:
                order.total_price = Decimal(str(data["total_price"]))
            order.notes = data.get("notes", order.notes)
            order.save(update_fields=["user_name", "status", "total_price", "notes", "updated_at"])

            OrderItem.objects.filter(order=order).delete()

            items = data.get("items", [])
            if items:
                product_ids = [i["product_id"] for i in items if "product_id" in i]
                prod_map = {
                    p.product_id: p for p in
                    Product.objects.filter(product_id__in=product_ids).only("id", "product_id")
                }

                new_items = []
                for item in items:
                    product = prod_map.get(item["product_id"]) or get_object_or_404(Product, product_id=item["product_id"])

                    try:
                        qty = int(item.get("quantity", 1))
                    except Exception:
                        qty = 1
                    unit_price = Decimal(str(item.get("unit_price", "0")))
                    total_price = Decimal(str(item.get("total_price", "0")))
                    attrs_delta = Decimal(str(item.get("attributes_price_delta", 0)))

                    if item.get("base_price") is not None:
                        base_price = Decimal(str(item["base_price"]))
                    else:
                        base_price = unit_price - attrs_delta
                        if base_price < 0:
                            base_price = Decimal("0")

                    selected_size = (item.get("selected_size") or "").strip()
                    selected_attributes = item.get("selected_attributes") or {}
                    selected_attributes_human = item.get("selected_attributes_human") or []
                    variant_signature = item.get("variant_signature") or ""

                    price_breakdown = {
                        "base_price": str(base_price),
                        "attributes_delta": str(attrs_delta),
                        "unit_price": str(unit_price),
                        "line_total": str(total_price),
                        "selected_size": selected_size,
                        "selected_attributes_human": selected_attributes_human,
                    }

                    new_items.append(OrderItem(
                        item_id=str(uuid.uuid4()),
                        order=order,
                        product=product,
                        quantity=qty,
                        unit_price=unit_price,
                        total_price=total_price,
                        selected_size=selected_size,
                        selected_attributes=selected_attributes,
                        selected_attributes_human=selected_attributes_human,
                        variant_signature=variant_signature,
                        attributes_price_delta=attrs_delta,
                        price_breakdown=price_breakdown,
                    ))

                OrderItem.objects.bulk_create(new_items, batch_size=500)

            delivery_data = data.get("delivery")
            if delivery_data:
                delivery_obj, _ = OrderDelivery.objects.get_or_create(order=order)

                raw = delivery_data.get("instructions", [])
                if isinstance(raw, str):
                    raw = [raw] if raw.strip() else []
                elif not isinstance(raw, list):
                    raw = []

                delivery_obj.name = delivery_data.get("name", delivery_obj.name)
                delivery_obj.email = delivery_data.get("email", delivery_obj.email)
                delivery_obj.phone = delivery_data.get("phone", delivery_obj.phone)
                delivery_obj.street_address = delivery_data.get("street_address", delivery_obj.street_address)
                delivery_obj.city = delivery_data.get("city", delivery_obj.city)
                delivery_obj.zip_code = delivery_data.get("zip_code", delivery_obj.zip_code)
                delivery_obj.instructions = raw
                delivery_obj.save(update_fields=[
                    "name", "email", "phone", "street_address", "city", "zip_code", "instructions", "updated_at"
                ])

            return Response({"message": "Order updated successfully", "order_id": order_id}, status=status.HTTP_200_OK)

        except Exception as e:
            print(traceback.format_exc())
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
