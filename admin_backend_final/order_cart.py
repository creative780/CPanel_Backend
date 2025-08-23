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
# Local Imports
from .models import *  # Consider specifying models instead of wildcard import
from .permissions import FrontendOnlyPermission


class SaveCartAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def _get_primary_cart(self, device_uuid: str) -> Cart:
        cart = Cart.objects.filter(device_uuid=device_uuid).order_by("-updated_at", "-created_at").first()
        if cart:
            # Optional: merge any accidental duplicates for same device_uuid
            dups = Cart.objects.filter(device_uuid=device_uuid).exclude(pk=cart.pk)
            if dups.exists():
                for dup in dups:
                    CartItem.objects.filter(cart=dup).update(cart=cart)
                    dup.delete()
            return cart
        return Cart.objects.create(cart_id=str(uuid.uuid4()), device_uuid=device_uuid)

    def _compute_attributes_delta_and_details(self, selected_attrs: dict) -> tuple[Decimal, list]:
        """
        selected_attrs looks like { "<parent_attr_id>": "<option_attr_id>", ... }
        Sum price_delta from each option attr and return human details.
        """
        total_delta = Decimal("0.00")
        details = []

        if not isinstance(selected_attrs, dict):
            return total_delta, details

        for parent_id, opt_id in selected_attrs.items():
            opt = Attribute.objects.filter(attr_id=opt_id).select_related("parent").first()
            parent = Attribute.objects.filter(attr_id=parent_id).first() if not (opt and opt.parent and opt.parent.attr_id == parent_id) else opt.parent

            price_delta = Decimal(str(opt.price_delta)) if (opt and opt.price_delta is not None) else Decimal("0.00")
            total_delta += price_delta

            details.append({
                "attribute_id": parent_id,
                "option_id": opt_id,
                "attribute_name": (parent.name if parent else parent_id),
                "option_label": (opt.label if opt else opt_id),
                "price_delta": str(price_delta)
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

            # Compute attribute price delta and human details
            attributes_delta, _human_details = self._compute_attributes_delta_and_details(selected_attributes)

            # Base price (use discounted if given, else normal)
            base_price = Decimal(str(product.discounted_price or product.price or 0))
            unit_price = base_price + attributes_delta

            # Signature ensures "same selection" merges
            # Use option IDs to ensure uniqueness even if labels change
            sig_parts = [f"size:{selected_size}"] + [
                f"{k}:{v}" for k, v in sorted(selected_attributes.items(), key=lambda x: x[0])
            ]
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
                cart_item.price_per_unit = unit_price  # keep latest pricing
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

    def _attr_humanize(self, sel: dict):
        """
        Return (details_list, delta_sum_decimal).
        details_list: [{attribute_name, option_label, price_delta}, ...]
        """
        details = []
        total_delta = Decimal("0.00")
        if not isinstance(sel, dict):
            return details, total_delta

        for parent_id, opt_id in sel.items():
            opt = Attribute.objects.filter(attr_id=opt_id).select_related("parent").first()
            parent = Attribute.objects.filter(attr_id=parent_id).first() if not (opt and opt.parent and opt.parent.attr_id == parent_id) else opt.parent

            price_delta = Decimal(str(opt.price_delta)) if (opt and opt.price_delta is not None) else Decimal("0.00")
            total_delta += price_delta
            details.append({
                "attribute_id": parent_id,
                "option_id": opt_id,
                "attribute_name": (parent.name if parent else parent_id),
                "option_label": (opt.label if opt else opt_id),
                "price_delta": str(price_delta)
            })
        return details, total_delta

    def _respond(self, request, device_uuid):
        if not device_uuid:
            return Response({"error": "Missing device UUID."}, status=status.HTTP_400_BAD_REQUEST)

        cart = Cart.objects.filter(device_uuid=device_uuid).order_by("-updated_at", "-created_at").first()
        if not cart:
            return Response({"cart_items": []}, status=status.HTTP_200_OK)

        cart_items = CartItem.objects.filter(cart=cart).select_related("product")
        response_data = []

        for item in cart_items:
            # Image (first linked product image)
            image_rel = Image.objects.filter(linked_table='product', linked_id=item.product.product_id).first()
            image_url = request.build_absolute_uri(image_rel.url) if image_rel and getattr(image_rel, "url", None) else None
            alt_text = getattr(image_rel, "alt_text", "") if image_rel else ""

            # Human-readable selections
            selections, attrs_delta = self._attr_humanize(item.selected_attributes or {})

            base_price = Decimal(str(item.product.discounted_price or item.product.price or 0))
            unit_price = base_price + attrs_delta
            line_total = unit_price * item.quantity

            # e.g. "Product1 (Paper Type: Simple, Size: 49)"
            selection_bits = []
            if item.selected_size:
                selection_bits.append(f"Size: {item.selected_size}")
            for d in selections:
                selection_bits.append(f"{d['attribute_name']}: {d['option_label']}")
            parenthetical = f" ({', '.join(selection_bits)})" if selection_bits else ""

            # e.g. "3 x $(4 + 0 + 5) = $27"
            # parts: actual base + each delta
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
                "selected_attributes": item.selected_attributes or {},  # raw ids mapping
                "selected_attributes_human": selections,                # names/labels + deltas
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

  
# delete_cart_item -> APIView (POST)
class DeleteCartItemAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')   # could be user id or device UUID
            product_id = data.get('product_id')

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

            cart_item = CartItem.objects.filter(cart=cart, product__product_id=product_id).first()
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
            data = json.loads(request.body or "{}")

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

            for item in items:
                for field in ["product_id", "quantity", "unit_price", "total_price"]:
                    if field not in item:
                        return Response({"error": f"Missing {field} in item"}, status=status.HTTP_400_BAD_REQUEST)

                product = get_object_or_404(Product, product_id=item["product_id"])

                qty = int(item.get("quantity", 1))
                unit_price = Decimal(str(item.get("unit_price", "0")))
                total_price = Decimal(str(item.get("total_price", "0")))
                attrs_delta = Decimal(str(item.get("attributes_price_delta", 0)))

                # base = unit - delta (unless explicitly provided)
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

                # store as strings to keep JSON clean/consistent
                price_breakdown = {
                    "base_price": str(base_price),
                    "attributes_delta": str(attrs_delta),
                    "unit_price": str(unit_price),
                    "line_total": str(total_price),
                    "selected_size": selected_size,
                    "selected_attributes_human": selected_attributes_human,
                }

                OrderItem.objects.create(
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

            # Normalize instructions to a list
            raw_instructions = delivery_data.get("instructions", [])
            if isinstance(raw_instructions, str):
                instructions = [raw_instructions] if raw_instructions.strip() else []
            elif isinstance(raw_instructions, list):
                instructions = raw_instructions
            else:
                instructions = []

            OrderDelivery.objects.create(
                delivery_id=str(uuid.uuid4()),
                order=order,
                name=delivery_data.get("name", user_name),
                email=email,  # may be None
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
            orders_data = []
            orders = Orders.objects.all().order_by('-created_at')

            for order in orders:
                order_items = (
                    OrderItem.objects
                    .filter(order=order)
                    .select_related('product')
                )

                try:
                    delivery = OrderDelivery.objects.get(order=order)
                    address = {
                        "street": delivery.street_address,
                        "city": delivery.city,
                        "zip": delivery.zip_code
                    }
                    email = delivery.email or ""
                except OrderDelivery.DoesNotExist:
                    address, email = {}, ""

                items_detail = []
                for it in order_items:
                    human = it.selected_attributes_human or []
                    tokens = []
                    if it.selected_size:
                        tokens.append(f"Size: {it.selected_size}")
                    for d in human:
                        tokens.append(f"{d.get('attribute_name','')}: {d.get('option_label','')}")
                    selection_str = ", ".join([t for t in tokens if t])

                    # math parts
                    try:
                        base = Decimal(it.price_breakdown.get("base_price", it.unit_price))
                    except Exception:
                        base = it.unit_price
                    deltas = []
                    for d in human:
                        try:
                            deltas.append(Decimal(d.get("price_delta", "0") or "0"))
                        except Exception:
                            deltas.append(Decimal("0"))

                    items_detail.append({
                        "product_id": it.product.product_id,
                        "product_name": it.product.title,
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
            data = json.loads(request.body or "{}")

            order_id = data.get("order_id")
            if not order_id:
                return Response({"error": "Missing order_id in request body"}, status=status.HTTP_400_BAD_REQUEST)

            order = get_object_or_404(Orders, order_id=order_id)

            # Header
            order.user_name = data.get("user_name", order.user_name)
            order.status = data.get("status", order.status)
            if data.get("total_price") is not None:
                order.total_price = Decimal(str(data["total_price"]))
            order.notes = data.get("notes", order.notes)
            order.save()

            # Rebuild items
            OrderItem.objects.filter(order=order).delete()

            for item in data.get("items", []):
                product = get_object_or_404(Product, product_id=item["product_id"])

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

                OrderItem.objects.create(
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

            # Delivery upsert
            delivery_data = data.get("delivery")
            if delivery_data:
                delivery_obj, _ = OrderDelivery.objects.get_or_create(order=order)

                raw_instructions = delivery_data.get("instructions", [])
                if isinstance(raw_instructions, str):
                    instructions = [raw_instructions] if raw_instructions.strip() else []
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
