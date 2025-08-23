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

# Django REST Framework
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .utilities import generate_custom_order_id
from .models import *  # models remain as-is
from .permissions import FrontendOnlyPermission


class SaveCartAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def _get_primary_cart(self, device_uuid: str) -> Cart:
        cart = Cart.objects.filter(device_uuid=device_uuid).order_by("-updated_at", "-created_at").first()
        if cart:
            # Merge duplicate carts in bulk (no per-row loops)
            dup_ids = list(
                Cart.objects.filter(device_uuid=device_uuid).exclude(pk=cart.pk).values_list("pk", flat=True)
            )
            if dup_ids:
                CartItem.objects.filter(cart_id__in=dup_ids).update(cart=cart)
                Cart.objects.filter(pk__in=dup_ids).delete()
            return cart
        return Cart.objects.create(cart_id=str(uuid.uuid4()), device_uuid=device_uuid)

    def _compute_attributes_delta_and_details(self, selected_attrs: dict) -> tuple[Decimal, list]:
        """
        selected_attrs: { "<parent_attr_id>": "<option_attr_id>", ... }
        Batch-lookup to avoid per-attribute queries.
        """
        total_delta = Decimal("0.00")
        details = []
        if not isinstance(selected_attrs, dict):
            return total_delta, details

        parent_ids = set(map(str, selected_attrs.keys()))
        opt_ids = set(map(str, selected_attrs.values()))
        if not opt_ids:
            return total_delta, details

        # Load all options with parent in one query, and parent attributes for names
        options = (
            Attribute.objects.filter(attr_id__in=list(opt_ids))
            .select_related("parent")
        )
        opt_map = {str(o.attr_id): o for o in options}

        known_parent_ids = {str(o.parent.attr_id) for o in options if getattr(o, "parent", None)}
        missing_parents = list(parent_ids - known_parent_ids)
        parent_map = {str(a.attr_id): a for a in Attribute.objects.filter(attr_id__in=missing_parents)} if missing_parents else {}

        for parent_id, opt_id in selected_attrs.items():
            opt = opt_map.get(str(opt_id))
            parent = getattr(opt, "parent", None)
            if not parent or str(parent.attr_id) != str(parent_id):
                parent = parent_map.get(str(parent_id))
            price_delta = Decimal(str(getattr(opt, "price_delta", "0") or "0"))
            total_delta += price_delta
            details.append({
                "attribute_id": str(parent_id),
                "option_id": str(opt_id),
                "attribute_name": (getattr(parent, "name", None) or str(parent_id)),
                "option_label": (getattr(opt, "label", None) or str(opt_id)),
                "price_delta": str(price_delta),
            })

        return total_delta, details

    def post(self, request):
        try:
            data = request.data if isinstance(request.data, dict) else json.loads(request.body or "{}")
            device_uuid = data.get("device_uuid") or request.headers.get("X-Device-UUID")
            if not device_uuid:
                return Response({"error": "Missing device UUID."}, status=status.HTTP_400_BAD_REQUEST)

            product_id = data.get('product_id')
            quantity = int(data.get('quantity', 1))
            selected_size = data.get("selected_size") or ""
            selected_attributes = data.get("selected_attributes") or {}

            product = get_object_or_404(Product, product_id=product_id)
            _ = get_object_or_404(ProductInventory, product=product)

            cart = self._get_primary_cart(device_uuid)

            attributes_delta, _human_details = self._compute_attributes_delta_and_details(selected_attributes)
            base_price = Decimal(str(product.discounted_price or product.price or 0))
            unit_price = base_price + attributes_delta

            sig_parts = [f"size:{selected_size}"] + [f"{k}:{v}" for k, v in sorted(selected_attributes.items(), key=lambda x: x[0])]
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
                    "attributes_price_delta": attributes_delta,
                }
            )

            if not created:
                cart_item.quantity += quantity
                cart_item.price_per_unit = unit_price
                cart_item.attributes_price_delta = attributes_delta
                cart_item.selected_size = selected_size
                cart_item.selected_attributes = selected_attributes
                cart_item.subtotal = unit_price * cart_item.quantity
                cart_item.save()

            return Response({"message": "Cart updated successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            print("❌ [SAVE_CART] Error:", str(e))
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ShowCartAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def _respond(self, request, device_uuid):
        if not device_uuid:
            return Response({"error": "Missing device UUID."}, status=status.HTTP_400_BAD_REQUEST)

        cart = Cart.objects.filter(device_uuid=device_uuid).order_by("-updated_at", "-created_at").first()
        if not cart:
            return Response({"cart_items": []}, status=status.HTTP_200_OK)

        cart_items = list(CartItem.objects.filter(cart=cart).select_related("product"))
        if not cart_items:
            return Response({"cart_items": []}, status=status.HTTP_200_OK)

        # Batch image lookup (first image per product)
        product_ids = [ci.product.product_id for ci in cart_items]
        image_qs = Image.objects.filter(linked_table='product', linked_id__in=product_ids).only("linked_id", "url", "alt_text", "id").order_by("id")
        first_image_by_product = {}
        for img in image_qs:
            pid = img.linked_id
            if pid not in first_image_by_product:
                first_image_by_product[pid] = img

        # Batch attribute lookup across all items
        all_parent_ids, all_opt_ids = set(), set()
        sel_by_item = []
        for item in cart_items:
            sel = item.selected_attributes or {}
            sel_by_item.append(sel)
            for pid, oid in sel.items():
                all_parent_ids.add(str(pid))
                all_opt_ids.add(str(oid))

        opt_map, parent_map = {}, {}
        if all_opt_ids:
            options = Attribute.objects.filter(attr_id__in=list(all_opt_ids)).select_related("parent").only(
                "attr_id", "label", "price_delta", "parent__attr_id", "parent__name"
            )
            opt_map = {str(o.attr_id): o for o in options}
            known_parent_ids = {str(o.parent.attr_id) for o in options if getattr(o, "parent", None)}
            missing_parent_ids = list(all_parent_ids - known_parent_ids)
            if missing_parent_ids:
                parents = Attribute.objects.filter(attr_id__in=missing_parent_ids).only("attr_id", "name")
                parent_map = {str(p.attr_id): p for p in parents}

        response_data = []
        for item, sel in zip(cart_items, sel_by_item):
            # Image
            img = first_image_by_product.get(item.product.product_id)
            image_url = request.build_absolute_uri(img.url) if img and getattr(img, "url", None) else None
            alt_text = getattr(img, "alt_text", "") if img else ""

            # Human-readable selections + delta sum
            selections = []
            attrs_delta = Decimal("0.00")
            if isinstance(sel, dict):
                for parent_id, opt_id in sel.items():
                    o = opt_map.get(str(opt_id))
                    parent = getattr(o, "parent", None)
                    if not parent or str(parent.attr_id) != str(parent_id):
                        parent = parent_map.get(str(parent_id))
                    price_delta = Decimal(str(getattr(o, "price_delta", "0") or "0"))
                    attrs_delta += price_delta
                    selections.append({
                        "attribute_id": str(parent_id),
                        "option_id": str(opt_id),
                        "attribute_name": (getattr(parent, "name", None) or str(parent_id)),
                        "option_label": (getattr(o, "label", None) or str(opt_id)),
                        "price_delta": str(price_delta),
                    })

            base_price = Decimal(str(item.product.discounted_price or item.product.price or 0))
            unit_price = base_price + attrs_delta
            line_total = unit_price * item.quantity

            selection_bits = []
            if item.selected_size:
                selection_bits.append(f"Size: {item.selected_size}")
            for d in selections:
                selection_bits.append(f"{d['attribute_name']}: {d['option_label']}")
            parenthetical = f" ({', '.join(selection_bits)})" if selection_bits else ""

            price_parts = [str(base_price)] + [d["price_delta"] for d in selections if d["price_delta"] not in ("0", "0.0", "0.00")]
            if not price_parts:
                price_parts = [str(base_price)]
            breakdown_str = f"{item.quantity} x $(" + " + ".join(price_parts) + f") = ${line_total}"

            response_data.append({
                "product_id": item.product.product_id,
                "product_name": item.product.title,
                "product_image": image_url,
                "alt_text": alt_text,
                "quantity": item.quantity,
                "selected_size": item.selected_size or "",
                "selected_attributes": sel or {},
                "selected_attributes_human": selections,
                "price_breakdown": {
                    "base_price": str(base_price),
                    "attributes_delta": str(attrs_delta),
                    "unit_price": str(unit_price),
                    "quantity": item.quantity,
                    "line_total": str(line_total),
                },
                "summary_line": f"{item.product.title}{parenthetical}: {breakdown_str}",
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
            user_id = data.get('user_id')  # user id or device UUID
            product_id = data.get('product_id')
            variant_signature = data.get('variant_signature') or ""

            if not user_id or not product_id:
                return Response({"error": "user_id and product_id are required."}, status=status.HTTP_400_BAD_REQUEST)

            DjangoUser = get_user_model()
            try:
                user = DjangoUser.objects.get(user_id=user_id)
                cart = Cart.objects.filter(user=user).first()
            except DjangoUser.DoesNotExist:
                cart = Cart.objects.filter(device_uuid=user_id).first()

            if not cart:
                return Response({"error": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)

            qs = CartItem.objects.filter(cart=cart, product__product_id=product_id)
            if variant_signature:
                qs = qs.filter(variant_signature=variant_signature)

            cart_item = qs.first()
            if not cart_item:
                return Response({"error": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)

            cart_item.delete()
            return Response({"message": "Cart item deleted successfully."}, status=status.HTTP_200_OK)
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
            if not isinstance(items, list) or len(items) == 0:
                return Response({"error": "No items provided"}, status=status.HTTP_400_BAD_REQUEST)

            # Batch product lookup
            product_ids = [str(x.get("product_id")) for x in items if x.get("product_id")]
            products = {p.product_id: p for p in Product.objects.filter(product_id__in=product_ids)}
            missing = [pid for pid in product_ids if pid not in products]
            if missing:
                return Response({"error": f"Products not found: {', '.join(missing)}"}, status=status.HTTP_400_BAD_REQUEST)

            order_items = []
            for item in items:
                product = products[str(item["product_id"])]
                qty = int(item.get("quantity", 1))
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

                order_items.append(
                    OrderItem(
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
                    )
                )

            OrderItem.objects.bulk_create(order_items, batch_size=100)

            # delivery
            raw_instructions = delivery_data.get("instructions", [])
            if isinstance(raw_instructions, str):
                instructions = [raw_instructions.strip()] if raw_instructions.strip() else []
            elif isinstance(raw_instructions, list):
                instructions = raw_instructions
            else:
                instructions = []

            OrderDelivery.objects.create(
                delivery_id=str(uuid.uuid4()),
                order=order,
                name=delivery_data.get("name", user_name),
                email=email,
                phone=delivery_data.get("phone", ""),
                street_address=delivery_data.get("street_address", ""),
                city=delivery_data.get("city", ""),
                zip_code=delivery_data.get("zip_code", ""),
                instructions=instructions,
            )

            return Response({"message": "Order saved successfully", "order_id": order_id}, status=status.HTTP_201_CREATED)

        except Product.DoesNotExist:
            return Response({"error": "One or more products not found"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(traceback.format_exc())
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ShowOrderAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def get(self, request):
        try:
            # Sort by order_date when present, then id as tiebreaker
            orders = list(Orders.objects.all().order_by('-order_date', '-id'))
            if not orders:
                return Response({"orders": []}, status=status.HTTP_200_OK)

            # Batch deliveries
            deliveries = {d.order_id: d for d in OrderDelivery.objects.filter(order__in=orders)}

            # Batch items (with product when it exists)
            order_items_qs = (
                OrderItem.objects
                .filter(order__in=orders)
                .select_related('product')
            )
            items_by_order = {}
            for it in order_items_qs:
                items_by_order.setdefault(it.order_id, []).append(it)

            orders_data = []
            for order in orders:
                order_items = items_by_order.get(order.id, [])
                delivery = deliveries.get(order.id)

                # ---- Safe address/email ----
                address = {"street": "", "city": "", "zip": ""}
                email = ""
                if delivery:
                    address = {
                        "street": delivery.street_address,
                        "city": delivery.city,
                        "zip": delivery.zip_code
                    }
                    email = delivery.email or ""

                items_detail = []
                for it in order_items:
                    # ---- Handle missing product rows safely ----
                    product_obj = getattr(it, "product", None)
                    if product_obj is None:
                        # Try to resolve lightly; if still missing, skip the item
                        # (alternatively, include a placeholder name)
                        try:
                            product_obj = Product.objects.only("product_id", "title").filter(pk=it.product_id).first()
                        except Exception:
                            product_obj = None
                    if product_obj is None:
                        # Skip orphaned rows to avoid 500s
                        continue

                    # ---- Normalize selected_attributes_human ----
                    human_raw = it.selected_attributes_human
                    human = []
                    if isinstance(human_raw, list):
                        human = human_raw
                    elif isinstance(human_raw, dict):
                        human = [human_raw]
                    elif isinstance(human_raw, str):
                        try:
                            parsed = json.loads(human_raw)
                            if isinstance(parsed, list):
                                human = parsed
                            elif isinstance(parsed, dict):
                                human = [parsed]
                        except Exception:
                            human = []

                    # ---- Normalize price_breakdown ----
                    pb_raw = it.price_breakdown
                    pb = {}
                    if isinstance(pb_raw, dict):
                        pb = pb_raw
                    elif isinstance(pb_raw, str):
                        try:
                            parsed_pb = json.loads(pb_raw)
                            if isinstance(parsed_pb, dict):
                                pb = parsed_pb
                        except Exception:
                            pb = {}

                    # ---- Build selection string safely ----
                    tokens = []
                    if it.selected_size:
                        tokens.append(f"Size: {it.selected_size}")
                    for d in human:
                        if isinstance(d, dict):
                            tokens.append(f"{d.get('attribute_name','')}: {d.get('option_label','')}")
                    selection_str = ", ".join([t for t in tokens if t])

                    # ---- Base & deltas (safe) ----
                    try:
                        base = Decimal(pb.get("base_price", it.unit_price))
                    except Exception:
                        base = it.unit_price

                    deltas = []
                    for d in human:
                        if isinstance(d, dict):
                            try:
                                deltas.append(Decimal(d.get("price_delta", "0") or "0"))
                            except Exception:
                                deltas.append(Decimal("0"))

                    items_detail.append({
                        "product_id": product_obj.product_id,
                        "product_name": product_obj.title,
                        "quantity": it.quantity,
                        "unit_price": str(it.unit_price),
                        "total_price": str(it.total_price),
                        "selection": selection_str,
                        "math": {
                            "base": str(base),
                            "deltas": [str(x) for x in deltas],
                        },
                        "variant_signature": it.variant_signature or "",
                    })

                # ---- Safe dates (some legacy rows might not have order_date) ----
                safe_dt = getattr(order, "order_date", None)
                date_str = safe_dt.strftime('%Y-%m-%d %H:%M:%S') if safe_dt else ""

                # ---- Safe total ----
                try:
                    total_float = float(order.total_price)
                except Exception:
                    total_float = 0.0

                orders_data.append({
                    "orderID": order.order_id,
                    "Date": date_str,
                    "UserName": order.user_name,
                    "item": {
                        "count": len(items_detail),
                        "names": [x["product_name"] for x in items_detail],
                        "detail": items_detail,
                    },
                    "total": total_float,
                    "status": order.status,
                    "Address": address,
                    "email": email,
                    "order_placed_on": date_str
                })

            return Response({"orders": orders_data}, status=status.HTTP_200_OK)
        except Exception as e:
            # Uncomment locally if you want the traceback in your console:
            # print(traceback.format_exc())
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
            order.save()

            OrderItem.objects.filter(order=order).delete()

            items = data.get("items", [])
            if items:
                product_ids = [str(x.get("product_id")) for x in items if x.get("product_id")]
                products = {p.product_id: p for p in Product.objects.filter(product_id__in=product_ids)}
                order_items = []

                for item in items:
                    product = products[str(item["product_id"])]
                    qty = int(item.get("quantity", 1))
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

                    order_items.append(
                        OrderItem(
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
                        )
                    )

                OrderItem.objects.bulk_create(order_items, batch_size=100)

            delivery_data = data.get("delivery")
            if delivery_data:
                delivery_obj, _ = OrderDelivery.objects.get_or_create(order=order)

                raw_instructions = delivery_data.get("instructions", [])
                if isinstance(raw_instructions, str):
                    instructions = [raw_instructions.strip()] if raw_instructions.strip() else []
                elif isinstance(raw_instructions, list):
                    instructions = raw_instructions
                else:
                    instructions = []

                delivery_obj.name = delivery_data.get("name", delivery_obj.name)
                delivery_obj.email = delivery_data.get("email", delivery_obj.email)
                delivery_obj.phone = delivery_data.get("phone", delivery_obj.phone)
                delivery_obj.street_address = delivery_data.get("street_address", delivery_obj.street_address)
                delivery_obj.city = delivery_data.get("city", delivery_obj.city)
                delivery_obj.zip_code = delivery_data.get("zip_code", delivery_obj.zip_code)
                delivery_obj.instructions = instructions
                delivery_obj.save()

            return Response({"message": "Order updated successfully", "order_id": order_id}, status=status.HTTP_200_OK)
        except Exception as e:
            print(traceback.format_exc())
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
