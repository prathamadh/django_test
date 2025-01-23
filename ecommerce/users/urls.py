from django.urls import path
from .views import *
from . import views

app_name = 'users'


urlpatterns=[
    path('',index),
    path('productlist',products),
    path('productdetails/<int:product_id>/', productdetails, name='product_details'),
    path('addtocart/<int:product_id>/', add_to_cart, name='add_to_cart'),

    # path('productdetails/<int:product_id>',productdetails),
    # path('addtocart/<int:product_id>/',add_to_cart),
    # path('addtocart/<int:product_id>/', add_to_cart, name='addtocart'),

    path('cart/',show_cart_items, name='cart'),
    path('removecart/<int:cart_id>',remove_cart_item),
    # path('orderform/<int:product_id>/<int:cart_id>',order_form),
    path('esewaform', views.EsewapaymentView.as_view(), name='esewaform'), # Class-based view
    path('esewaverify',views.esewa_verify, name='esewa_verify'),  # Function-based view with URL parameters
    path('myorder/',my_order,name='my_order'),
    
    # Add new path for checkout (bulk order handling)
    path('checkout/', views.checkout, name='checkout'),
    path('order/confirmation/', views.order_confirmation, name='order_confirmation'),
    path('category/<int:category_id>/products/', show_category, name='category_product'),
    path('add_to_wishlist/<int:product_id>/', add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/', views.show_wishlist_items, name='show_wishlist_items'),
    path('removewishlist/<int:wishlist_id>/', views.remove_wishlist_item, name='remove_wishlist_item'),
    path('profile/', views.profile, name='profile'),
    path('test/', TestView.as_view(), name='test'),









]