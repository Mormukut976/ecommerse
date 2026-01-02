from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from cart.utils import clear_cart, get_cart_items

from .forms import CheckoutForm
from .models import Order, OrderItem


def _build_tracking_steps(order_status: str):
    progress = {
        Order.Status.PLACED: 0,
        Order.Status.PENDING_PAYMENT: 1,
        Order.Status.PAYMENT_SUBMITTED: 2,
        Order.Status.PAID: 3,
        Order.Status.READY_TO_GO: 4,
        Order.Status.SHIPPED: 5,
        Order.Status.OUT_FOR_DELIVERY: 6,
        Order.Status.ARRIVED: 7,
        Order.Status.DELIVERED: 8,
    }

    steps = [
        Order.Status.PLACED,
        Order.Status.PENDING_PAYMENT,
        Order.Status.PAYMENT_SUBMITTED,
        Order.Status.PAID,
        Order.Status.READY_TO_GO,
        Order.Status.SHIPPED,
        Order.Status.OUT_FOR_DELIVERY,
        Order.Status.ARRIVED,
        Order.Status.DELIVERED,
    ]

    if order_status == Order.Status.CANCELLED:
        progress[Order.Status.CANCELLED] = 0
        steps.append(Order.Status.CANCELLED)

    current = progress.get(order_status, 0)

    tracking_steps = []
    for status in steps:
        tracking_steps.append(
            {
                'value': status,
                'label': Order.Status(status).label,
                'done': current >= progress[status],
                'current': order_status == status,
            }
        )

    return tracking_steps


@login_required
def checkout(request):
    items, subtotal = get_cart_items(request)
    if not items:
        return redirect('cart:detail')

    shipping_fee = Decimal('0.00')
    total = subtotal + shipping_fee

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order_status = Order.Status.PENDING_PAYMENT
            manual_payment_method = form.cleaned_data.get('manual_payment_method')

            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user,
                    full_name=form.cleaned_data['full_name'],
                    phone=form.cleaned_data['phone'],
                    address_line1=form.cleaned_data['address_line1'],
                    address_line2=form.cleaned_data.get('address_line2', ''),
                    city=form.cleaned_data['city'],
                    state=form.cleaned_data['state'],
                    pincode=form.cleaned_data['pincode'],
                    payment_method=Order.PaymentMethod.MANUAL,
                    manual_payment_method=manual_payment_method,
                    status=order_status,
                    subtotal=subtotal,
                    shipping_fee=shipping_fee,
                    total=total,
                )

                if not order.order_code:
                    order.save(update_fields=['order_code'])

                for item in items:
                    product = item['product']
                    qty = item['quantity']
                    unit_price = product.selling_price
                    line_total = unit_price * qty

                    size = item.get('size')
                    size_label = size.label if size else ''

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        size_label=size_label,
                        product_name=product.name,
                        unit_price=unit_price,
                        quantity=qty,
                        line_total=line_total,
                    )

            clear_cart(request)

            return redirect('payments:manual_payment', order_id=order.id)
    else:
        form = CheckoutForm()

    return render(
        request,
        'orders/checkout.html',
        {
            'form': form,
            'items': items,
            'subtotal': subtotal,
            'shipping_fee': shipping_fee,
            'total': total,
        },
    )


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items')
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related('items').select_related('manual_payment_method'),
        id=order_id,
        user=request.user,
    )

    try:
        payment = order.payment
    except ObjectDoesNotExist:
        payment = None

    tracking_steps = _build_tracking_steps(order.status)

    return render(
        request,
        'orders/order_detail.html',
        {
            'order': order,
            'payment': payment,
            'tracking_steps': tracking_steps,
        },
    )


@login_required
def thank_you(request, order_id):
    order = get_object_or_404(Order.objects.prefetch_related('items'), id=order_id, user=request.user)
    if order.status not in {
        Order.Status.PAID,
        Order.Status.READY_TO_GO,
        Order.Status.SHIPPED,
        Order.Status.OUT_FOR_DELIVERY,
        Order.Status.ARRIVED,
        Order.Status.DELIVERED,
    }:
        return redirect('orders:order_detail', order_id=order.id)
    return render(request, 'orders/thank_you.html', {'order': order})
