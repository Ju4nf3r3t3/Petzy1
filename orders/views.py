from django.http import HttpResponse
from reportlab.pdfgen import canvas
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
from cart.models import Cart, CartItem
from products.models import Producto
from .models import Order, OrderItem

@login_required
def order_list(request):
    orders = Order.objects.filter(usuario=request.user).order_by("-fecha")
    return render(request, "orders/order_list.html", {"orders": orders})


@login_required
def checkout(request):
    cart, created = Cart.objects.get_or_create(usuario=request.user)
    items = cart.items.select_related("producto")

    # Verificar si el carrito está vacío
    if not items.exists():
        messages.warning(request, "Tu carrito está vacío")
        return redirect('cart:detail')

    if request.method == "POST":
        # Verificar stock antes de crear la orden
        for item in items:
            if item.cantidad > item.producto.stock:
                messages.error(request, f"No hay suficiente stock de {item.producto.nombre}")
                return redirect('cart:detail')

        # Crear orden
        orden = Order.objects.create(usuario=request.user, estado="pendiente")
        total = Decimal('0.00')

        for item in items:
            # Crear item de la orden
            OrderItem.objects.create(
                order=orden,
                producto=item.producto,
                cantidad=item.cantidad,
                precio_unitario=item.producto.precio,
            )
            # Actualizar stock del producto
            item.producto.stock -= item.cantidad
            item.producto.save()

            total += item.producto.precio * item.cantidad

        # Guardar total de la orden
        orden.total = total
        orden.save()

        # Vaciar carrito (PERO PRIMERO guardamos los items en una variable)
        items_list = list(items)  # Guardamos una copia antes de borrar
        items.delete()  # Ahora sí borramos

        messages.success(request, f"¡Orden #{orden.id} creada exitosamente!")
        return redirect("orders:confirm", order_id=orden.id)

    # Calcular total para el template
    total = sum(Decimal(str(item.producto.precio)) * item.cantidad for item in items)
    return render(request, "orders/checkout.html", {
        "items": items,
        "total": total,
        "shipping_cost": Decimal('5.00'),
        "total_with_shipping": total + Decimal('5.00')
    })


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