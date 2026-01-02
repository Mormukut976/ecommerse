def cart_item_count(request):
    cart = request.session.get('cart', {})
    if not isinstance(cart, dict):
        return {'cart_item_count': 0}

    count = 0
    for qty in cart.values():
        try:
            count += int(qty)
        except Exception:
            continue

    return {'cart_item_count': count}
