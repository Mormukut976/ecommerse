from django.urls import path

from . import views

app_name = 'payments'

urlpatterns = [
    path('manual/<int:order_id>/', views.manual_payment, name='manual_payment'),
]
