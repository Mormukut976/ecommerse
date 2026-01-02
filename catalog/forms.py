from django import forms


class ProductReviewForm(forms.Form):
    name = forms.CharField(
        required=False,
        max_length=120,
        label='Your Name',
    )
    rating = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        initial='5',
        label='Rating (1-5)',
    )
    comment = forms.CharField(
        required=False,
        label='Review',
        widget=forms.Textarea(attrs={'rows': 3}),
    )


class ContactUsForm(forms.Form):
    ISSUE_CHOICES = [
        ('DELIVERY', 'Delivery complaint'),
        ('PRODUCT', 'Product issue'),
        ('PAYMENT', 'Payment issue'),
        ('OTHER', 'Other'),
    ]

    name = forms.CharField(max_length=120, label='Your Name')
    email = forms.EmailField(label='Your Email')
    issue_type = forms.ChoiceField(choices=ISSUE_CHOICES, label='Reason')
    order_code = forms.CharField(required=False, max_length=20, label='Order Code (optional)')
    message = forms.CharField(label='Message', widget=forms.Textarea(attrs={'rows': 5}))
