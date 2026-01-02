from django.urls import path

from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('category/<slug:slug>/', views.product_list, name='category'),
    path('contact/', views.contact_us, name='contact_us'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('product/<slug:slug>/review/', views.product_review_create, name='product_review_create'),
]
