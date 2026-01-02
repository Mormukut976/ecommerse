import base64
from io import BytesIO
from urllib.parse import urlencode

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from orders.models import Order

from .models import Payment


class ManualPaymentForm(forms.Form):
    manual_reference = forms.CharField(
        max_length=120,
        label='UTR / Transaction ID',
        help_text='Enter the UTR/Transaction ID after completing the payment.',
    )
    manual_proof = forms.ImageField(required=False)


def _build_upi_uri(*, upi_id: str, payee_name: str, amount, note: str):
    params = {
        'pa': upi_id,
        'pn': payee_name,
        'am': str(amount),
        'tn': note,
        'cu': 'INR',
    }
    return f"upi://pay?{urlencode(params)}"


@login_required
def manual_payment(request, order_id):
    order = get_object_or_404(Order.objects.select_related('manual_payment_method'), id=order_id, user=request.user)

    if order.payment_method != Order.PaymentMethod.MANUAL:
        return redirect('orders:order_detail', order_id=order.id)

    if order.status == Order.Status.PAID:
        messages.info(request, 'Order already paid.')
        return redirect('orders:order_detail', order_id=order.id)

    if order.status not in {Order.Status.PENDING_PAYMENT, Order.Status.PAYMENT_SUBMITTED}:
        return redirect('orders:order_detail', order_id=order.id)

    payment = Payment.objects.filter(order=order).first()
    form = ManualPaymentForm(
        request.POST or None,
        request.FILES or None,
        initial={'manual_reference': payment.manual_reference if payment else ''},
    )

    if request.method == 'POST' and form.is_valid():
        payment, _ = Payment.objects.get_or_create(order=order, defaults={'amount': order.total})
        payment.provider = Payment.Provider.MANUAL
        payment.amount = order.total
        payment.manual_reference = form.cleaned_data['manual_reference']
        if form.cleaned_data.get('manual_proof'):
            payment.manual_proof = form.cleaned_data['manual_proof']
        payment.status = Payment.Status.SUBMITTED
        payment.save()

        order.status = Order.Status.PAYMENT_SUBMITTED
        order.save()

        messages.success(request, 'Payment submitted. We will verify and confirm soon.')
        return redirect('orders:order_detail', order_id=order.id)

    payment_method = order.manual_payment_method
    qr_data_uri = None
    upi_uri = None
    if payment_method and payment_method.method_type == 'QR' and payment_method.upi_id:
        upi_uri = _build_upi_uri(
            upi_id=payment_method.upi_id,
            payee_name='Shope in home',
            amount=order.total,
            note=f"Order #{order.id}",
        )
        try:
            import qrcode

            qr_img = qrcode.make(upi_uri)
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            qr_data_uri = 'data:image/png;base64,' + base64.b64encode(buffer.getvalue()).decode('utf-8')
        except Exception:
            qr_data_uri = None

    return render(
        request,
        'payments/manual_payment.html',
        {
            'order': order,
            'payment_method': payment_method,
            'payment': payment,
            'form': form,
            'qr_data_uri': qr_data_uri,
            'upi_uri': upi_uri,
        },
    )
