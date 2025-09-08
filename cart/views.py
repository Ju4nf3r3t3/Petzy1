from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from products.models import Producto
from .models import Cart, CartItem
from django.contrib import messages
from decimal import Decimal  # ← Importa Decimal


@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(usuario=request.user)
    items = cart.items.select_related("producto")

    # Calcular totales - Usar Decimal para consistencia
    subtotal = Decimal('0.00')
    for item in items:
        item.subtotal = item.producto.precio * item.cantidad
        subtotal += item.subtotal

    shipping_cost = Decimal('5.00') if subtotal > Decimal('0.00') else Decimal('0.00')  # Usar Decimal
    total = subtotal + shipping_cost

    return render(request, "cart/cart_detail.html", {
        "cart": cart,
        "cart_items": items,
        "cart_total": subtotal,
        "shipping_cost": shipping_cost,
        "total_with_shipping": total
    })


@login_required
def add_to_cart(request, product_id):
    cart, created = Cart.objects.get_or_create(usuario=request.user)
    producto = get_object_or_404(Producto, pk=product_id)

    cantidad = int(request.POST.get('cantidad', 1))

    # Verificar stock
    if cantidad > producto.stock:
        messages.error(request, f"No hay suficiente stock de {producto.nombre}")
        return redirect('products:detail', pk=producto.pk)

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        producto=producto,
        defaults={'cantidad': cantidad}
    )

    if not created:
        # Verificar que no exceda el stock al actualizar
        if item.cantidad + cantidad > producto.stock:
            messages.error(request, f"No hay suficiente stock de {producto.nombre}")
            return redirect('products:detail', pk=producto.pk)
        item.cantidad += cantidad
        item.save()

    messages.success(request, f"{producto.nombre} agregado al carrito")
    return redirect("cart:detail")


@login_required
def remove_from_cart(request, item_id):
    cart = get_object_or_404(Cart, usuario=request.user)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    item.delete()
    messages.success(request, "Producto eliminado del carrito")
    return redirect("cart:detail")


@login_required
def update_cart(request, product_id):
    cart = get_object_or_404(Cart, usuario=request.user)
    producto = get_object_or_404(Producto, pk=product_id)
    item = get_object_or_404(CartItem, cart=cart, producto=producto)

    cantidad = int(request.POST.get('cantidad', 1))

    # Verificar stock
    if cantidad > producto.stock:
        messages.error(request, f"No hay suficiente stock de {producto.nombre}")
        return redirect('cart:detail')

    if cantidad <= 0:
        item.delete()
        messages.success(request, "Producto eliminado del carrito")
    else:
        item.cantidad = cantidad
        item.save()
        messages.success(request, "Cantidad actualizada")

    return redirect("cart:detail")