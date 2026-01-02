from django import forms

from payments.models import PaymentMethod

from .models import Order


class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=200)
    phone = forms.CharField(max_length=20)

    address_line1 = forms.CharField(max_length=255)
    address_line2 = forms.CharField(max_length=255, required=False)
    city = forms.CharField(max_length=120)
    state = forms.CharField(max_length=120)
    pincode = forms.CharField(max_length=12)
    manual_payment_method = forms.ModelChoiceField(
        queryset=PaymentMethod.objects.none(),
        required=False,
        empty_label=None,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        qs = PaymentMethod.objects.filter(is_active=True)
        field = self.fields['manual_payment_method']
        field.queryset = qs

        def label_from_instance(obj):
            label = obj.name
            if obj.method_type == PaymentMethod.Type.QR:
                return label
            details = []
            if obj.upi_id:
                details.append(obj.upi_id)
            elif obj.account_number:
                tail = obj.account_number[-4:]
                if tail:
                    details.append(f"A/c ending {tail}")
            if details:
                label = f"{label} ({' | '.join(details)})"
            return label

        field.label_from_instance = label_from_instance

        if qs.exists() and not self.is_bound:
            self.initial.setdefault('manual_payment_method', qs.first())

    def clean(self):
        cleaned_data = super().clean()
        if not self.fields['manual_payment_method'].queryset.exists():
            self.add_error('manual_payment_method', 'No payment options are configured. Please contact support.')
            return cleaned_data

        if not cleaned_data.get('manual_payment_method'):
            self.add_error('manual_payment_method', 'Select a payment option')
        return cleaned_data
