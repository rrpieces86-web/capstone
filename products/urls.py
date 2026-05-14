from django.urls import path
from .views import (
    ProductListView,
    ProductDetailView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView
)
from . import views
urlpatterns = [
    path('list/', ProductListView.as_view(), name='product_list'),
    path('detail/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('new/', ProductCreateView.as_view(), name='new_product'),
    path('edit/<int:pk>/', ProductUpdateView.as_view(), name='edit_product'),
    path('delete/<int:pk>/', ProductDeleteView.as_view(), name='delete_product'),
    path("add_to_cart/", views.add_to_cart, name="cart_add"),
    path("cart/", views.cart, name="cart"),
    path("cart/remove/<int:item_id>/", views.remove_from_cart, name="cart_remove"),
    path("checkout/", views.checkout, name="checkout"),
    path("order/confirmation/", views.order_confirmation, name="order_confirmation"),
]