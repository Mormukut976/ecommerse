from django.conf import settings
from django.db.models import Prefetch
from django.contrib import messages
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect
from django.templatetags.static import static
from django.views.decorators.http import require_POST

from .forms import ContactUsForm, ProductReviewForm
from .models import Category, Product, ProductReview, ProductSize


def product_list(request, slug=None):
    categories = Category.objects.filter(is_active=True)
    products = Product.objects.filter(is_active=True).select_related('category').prefetch_related(
        Prefetch('sizes', queryset=ProductSize.objects.filter(is_active=True), to_attr='active_sizes')
    )
    selected_category = None

    if slug:
        selected_category = get_object_or_404(Category, slug=slug, is_active=True)
        products = products.filter(category=selected_category)

    query = (request.GET.get('q') or '').strip()
    if query:
        products = products.filter(name__icontains=query)

    return render(
        request,
        'catalog/product_list.html',
        {
            'categories': categories,
            'products': products,
            'selected_category': selected_category,
            'query': query,
        },
    )


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.prefetch_related(
            Prefetch('sizes', queryset=ProductSize.objects.filter(is_active=True), to_attr='active_sizes'),
            Prefetch(
                'reviews',
                queryset=ProductReview.objects.filter(is_active=True).select_related('user'),
                to_attr='active_reviews',
            ),
        ),
        slug=slug,
        is_active=True,
    )
    gallery_images = [img for img in [product.image, product.image2, product.image3, product.image4] if img]
    return render(
        request,
        'catalog/product_detail.html',
        {
            'product': product,
            'sizes': product.active_sizes,
            'reviews': getattr(product, 'active_reviews', []),
            'review_form': ProductReviewForm(),
            'gallery_images': gallery_images,
        },
    )


@require_POST
def product_review_create(request, slug):
    product = get_object_or_404(
        Product.objects.prefetch_related(
            Prefetch('sizes', queryset=ProductSize.objects.filter(is_active=True), to_attr='active_sizes'),
            Prefetch(
                'reviews',
                queryset=ProductReview.objects.filter(is_active=True).select_related('user'),
                to_attr='active_reviews',
            ),
        ),
        slug=slug,
        is_active=True,
    )
    gallery_images = [img for img in [product.image, product.image2, product.image3, product.image4] if img]

    form = ProductReviewForm(request.POST)
    if form.is_valid():
        is_auth = request.user.is_authenticated
        name = (form.cleaned_data.get('name') or '').strip()
        if is_auth:
            name = ''
        elif not name:
            name = 'Customer'

        ProductReview.objects.create(
            product=product,
            user=request.user if is_auth else None,
            name=name,
            rating=int(form.cleaned_data['rating']),
            comment=form.cleaned_data.get('comment', ''),
            is_active=True,
        )

        messages.success(request, 'Review submitted.')
        return redirect('catalog:product_detail', slug=product.slug)

    messages.error(request, 'Please correct the errors below.')
    return render(
        request,
        'catalog/product_detail.html',
        {
            'product': product,
            'sizes': product.active_sizes,
            'reviews': getattr(product, 'active_reviews', []),
            'review_form': form,
            'gallery_images': gallery_images,
        },
    )


def contact_us(request):
    contact_email = getattr(settings, 'CONTACT_TO_EMAIL', 'tredarssr@gmail.com')
    whatsapp_chat_url = getattr(settings, 'WHATSAPP_CHAT_URL', '')
    whatsapp_qr_static_path = getattr(settings, 'WHATSAPP_QR_STATIC_PATH', '')

    whatsapp_qr_url = None
    if whatsapp_qr_static_path:
        if whatsapp_qr_static_path.startswith(('http://', 'https://')):
            whatsapp_qr_url = whatsapp_qr_static_path
        else:
            whatsapp_qr_url = static(whatsapp_qr_static_path)

    if request.method == 'POST':
        form = ContactUsForm(request.POST)
        if form.is_valid():
            issue_value = form.cleaned_data['issue_type']
            issue_label = dict(form.fields['issue_type'].choices).get(issue_value, issue_value)

            name = (form.cleaned_data.get('name') or '').strip()
            email = (form.cleaned_data.get('email') or '').strip()
            order_code = (form.cleaned_data.get('order_code') or '').strip()
            message_text = (form.cleaned_data.get('message') or '').strip()

            subject_parts = [f"Contact: {issue_label}"]
            if order_code:
                subject_parts.append(f"Order {order_code}")
            subject = ' | '.join(subject_parts)

            body_lines = [
                f"Name: {name}",
                f"Email: {email}",
                f"Reason: {issue_label}",
            ]
            if order_code:
                body_lines.append(f"Order Code: {order_code}")
            body_lines.extend(['', 'Message:', message_text])
            body = '\n'.join(body_lines)

            email_message = EmailMessage(
                subject=subject,
                body=body,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', ''),
                to=[contact_email],
                reply_to=[email] if email else [],
            )

            try:
                email_message.send(fail_silently=False)
            except Exception:
                messages.error(request, 'Could not send your message right now. Please try again later.')
            else:
                messages.success(request, 'Message sent. We will contact you soon.')
                return redirect('catalog:contact_us')
    else:
        initial = {}
        if request.user.is_authenticated:
            full_name = (request.user.get_full_name() or '').strip()
            if full_name:
                initial['name'] = full_name
            user_email = (getattr(request.user, 'email', '') or '').strip()
            if user_email:
                initial['email'] = user_email
        form = ContactUsForm(initial=initial)

    return render(
        request,
        'pages/contact_us.html',
        {
            'form': form,
            'contact_email': contact_email,
            'whatsapp_qr_url': whatsapp_qr_url,
            'whatsapp_chat_url': whatsapp_chat_url,
        },
    )
