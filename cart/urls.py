from django.urls import path

from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail, name='detail'),
    path('add/<int:product_id>/', views.cart_add, name='add'),
    path('set/<str:item_key>/', views.cart_set_quantity, name='set_quantity'),
    path('remove/<str:item_key>/', views.cart_remove, name='remove'),
    path('clear/', views.cart_clear, name='clear'),
]
