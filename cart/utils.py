from decimal import Decimal

from catalog.models import Product, ProductSize

CART_SESSION_KEY = 'cart'


def get_cart(request):
    cart = request.session.get(CART_SESSION_KEY)
    if not isinstance(cart, dict):
        cart = {}
    return cart


def save_cart(request, cart):
    request.session[CART_SESSION_KEY] = cart
    request.session.modified = True


def clear_cart(request):
    request.session[CART_SESSION_KEY] = {}
    request.session.modified = True


def get_cart_items(request):
    cart = get_cart(request)

    product_ids = []
    size_ids = []
    for key in cart.keys():
        pid_part = key
        size_part = '0'
        if ':' in key:
            pid_part, size_part = key.split(':', 1)

        try:
            pid_int = int(pid_part)
        except Exception:
            continue

        try:
            size_int = int(size_part)
        except Exception:
            size_int = 0

        product_ids.append(pid_int)
        if size_int > 0:
            size_ids.append(size_int)

    products = Product.objects.filter(id__in=product_ids, is_active=True)
    products_by_id = {p.id: p for p in products}

    sizes = ProductSize.objects.filter(product_id__in=product_ids, is_active=True).order_by('sort_order', 'label')
    sizes_by_id = {s.id: s for s in sizes}
    sizes_by_product_id = {}
    for s in sizes:
        sizes_by_product_id.setdefault(s.product_id, []).append(s)

    items = []
    subtotal = Decimal('0.00')
    cleaned_cart = {}
    items_by_key = {}

    for key, qty in cart.items():
        pid_part = key
        size_part = '0'
        if ':' in key:
            pid_part, size_part = key.split(':', 1)

        try:
            pid_int = int(pid_part)
        except Exception:
            continue

        try:
            size_int = int(size_part)
        except Exception:
            size_int = 0

        try:
            qty_int = int(qty)
        except Exception:
            qty_int = 0

        product = products_by_id.get(pid_int)
        if not product:
            continue

        size = None
        if size_int > 0:
            size = sizes_by_id.get(size_int)
            if not size or size.product_id != product.id:
                size = None
                size_int = 0

        if size_int == 0:
            default_sizes = sizes_by_product_id.get(product.id) or []
            if default_sizes:
                size = default_sizes[0]
                size_int = size.id

        if qty_int > 0:
            item_key = f"{product.id}:{size_int}"
            cleaned_cart[item_key] = int(cleaned_cart.get(item_key, 0)) + qty_int

            existing = items_by_key.get(item_key)
            if existing:
                existing['quantity'] += qty_int
            else:
                items_by_key[item_key] = {'product': product, 'size': size, 'size_id': size_int, 'quantity': qty_int}

    for item_key, item in items_by_key.items():
        unit_price = item['product'].selling_price
        line_total = unit_price * item['quantity']
        subtotal += line_total
        item['line_total'] = line_total
        item['key'] = item_key
        items.append(item)

    if cleaned_cart != cart:
        save_cart(request, cleaned_cart)

    return items, subtotal
