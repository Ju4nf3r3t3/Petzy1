from django.http import HttpResponse
from reportlab.pdfgen import canvas
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import ensure_csrf_cookie
from decimal import Decimal
from cart.models import Cart
from .forms import CheckoutForm
from .models import Order, OrderItem

@login_required
def order_list(request):
    orders = Order.objects.filter(usuario=request.user).order_by("-fecha")
    return render(request, "orders/order_list.html", {"orders": orders})


@login_required
@ensure_csrf_cookie
def checkout(request):
    cart, created = Cart.objects.get_or_create(usuario=request.user)
    items_queryset = cart.items.select_related("producto")

    if not items_queryset.exists():
        messages.warning(request, _("Tu carrito está vacío"))
        return redirect("cart:detail")

    items = list(items_queryset)

    # Verificar stock antes de procesar la orden
    for item in items:
        if item.cantidad > item.producto.stock:
            messages.error(
                request,
                _("No hay suficiente stock de %(product)s") % {"product": item.producto.nombre},
            )
            return redirect("cart:detail")

    subtotal = sum(
        (item.producto.precio * item.cantidad for item in items),
        Decimal("0.00"),
    )
    shipping_cost = Decimal("5.00")
    total_with_shipping = subtotal + shipping_cost

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            orden = Order.objects.create(usuario=request.user, estado="pendiente")
            total = Decimal("0.00")

            for item in items:
                OrderItem.objects.create(
                    order=orden,
                    producto=item.producto,
                    cantidad=item.cantidad,
                    precio_unitario=item.producto.precio,
                )
                item.producto.stock -= item.cantidad
                item.producto.save()
                total += item.producto.precio * item.cantidad

            orden.total = total
            orden.save()

            cart.items.filter(pk__in=[item.pk for item in items]).delete()

            messages.success(
                request,
                _("¡Orden #%(order_id)s creada exitosamente!") % {"order_id": orden.id},
            )
            return redirect("orders:confirm", order_id=orden.id)

        messages.error(
            request,
            _("Por favor corrige los errores en el formulario de pago."),
        )
    else:
        initial_data = {
            "email": request.user.email,
        }
        full_name = request.user.get_full_name()
        if full_name:
            initial_data["nombre"] = full_name
        elif getattr(request.user, "username", ""):
            initial_data["nombre"] = request.user.username
        form = CheckoutForm(initial=initial_data)

    return render(
        request,
        "orders/checkout.html",
        {
            "items": items,
            "subtotal": subtotal,
            "shipping_cost": shipping_cost,
            "total_with_shipping": total_with_shipping,
            "form": form,
        },
    )


@login_required
def confirm(request, order_id):
    order = get_object_or_404(Order, pk=order_id, usuario=request.user)
    return render(request, "orders/confirm.html", {"order": order})


def generar_factura(request, pk):
    order = Order.objects.get(pk=pk)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="factura_{order.id}.pdf"'

    p = canvas.Canvas(response)
    p.drawString(100, 800, f"Factura Pedido #{order.id}")
    p.drawString(100, 780, f"Cliente: {order.usuario.username}")

    y = 750
    for item in order.items.all():
        p.drawString(100, y, f"{item.producto.nombre} - Cant: {item.cantidad} - Precio: {item.precio_unitario}")
        y -= 20

    p.drawString(100, y-20, f"Total: {order.total}")
    p.showPage()
    p.save()

    return response
