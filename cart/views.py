from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from catalog.models import Product, ProductSize

from .utils import clear_cart, get_cart, get_cart_items, save_cart


def cart_detail(request):
    items, subtotal = get_cart_items(request)
    return render(request, 'cart/detail.html', {'items': items, 'subtotal': subtotal})


@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)

    try:
        qty = int(request.POST.get('quantity', 1))
    except Exception:
        qty = 1

    qty = max(1, qty)

    size_id = request.POST.get('size_id')
    try:
        size_int = int(size_id) if size_id else 0
    except Exception:
        size_int = 0

    if size_int > 0:
        size_exists = ProductSize.objects.filter(id=size_int, product=product, is_active=True).exists()
        if not size_exists:
            size_int = 0

    if size_int == 0:
        default_size = (
            ProductSize.objects.filter(product=product, is_active=True).order_by('sort_order', 'label').first()
        )
        if default_size:
            size_int = default_size.id

    cart = get_cart(request)
    item_key = f"{product.id}:{size_int}"
    cart[item_key] = int(cart.get(item_key, 0)) + qty
    save_cart(request, cart)

    return redirect('cart:detail')


@require_POST
def cart_set_quantity(request, item_key):
    pid_part = item_key
    size_part = '0'
    if ':' in item_key:
        pid_part, size_part = item_key.split(':', 1)

    try:
        product_id = int(pid_part)
    except Exception:
        return redirect('cart:detail')

    try:
        size_int = int(size_part)
    except Exception:
        size_int = 0

    get_object_or_404(Product, id=product_id, is_active=True)

    if size_int > 0:
        size_exists = ProductSize.objects.filter(id=size_int, product_id=product_id, is_active=True).exists()
        if not size_exists:
            size_int = 0

    try:
        qty = int(request.POST.get('quantity', 1))
    except Exception:
        qty = 1

    cart = get_cart(request)
    normalized_key = f"{product_id}:{size_int}"

    if qty <= 0:
        cart.pop(normalized_key, None)
        if item_key != normalized_key:
            cart.pop(item_key, None)
    else:
        cart[normalized_key] = qty
        if item_key != normalized_key:
            cart.pop(item_key, None)

    save_cart(request, cart)
    return redirect('cart:detail')


@require_POST
def cart_remove(request, item_key):
    cart = get_cart(request)
    cart.pop(item_key, None)
    save_cart(request, cart)
    return redirect('cart:detail')


@require_POST
def cart_clear(request):
    clear_cart(request)
    return redirect('cart:detail')
