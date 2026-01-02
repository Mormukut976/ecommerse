from django.urls import path

from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('checkout/', views.checkout, name='checkout'),
    path('<int:order_id>/', views.order_detail, name='order_detail'),
    path('<int:order_id>/thank-you/', views.thank_you, name='thank_you'),
]
