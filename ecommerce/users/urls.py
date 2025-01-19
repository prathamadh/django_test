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
    path('esewaform/<int:order_id>/<int:cart_id>/', views.EsewaPaymentView, name='esewaform'),  # Class-based view
    path('esewaverify/<int:order_id>/<int:cart_id>/', views.esewa_verify, name='esewa_verify'),  # Function-based view with URL parameters
    path('myorder/',my_order),
    
    # Add new path for checkout (bulk order handling)
    path('checkout/', views.checkout, name='checkout'),
    path('order/confirmation/', views.order_confirmation, name='order_confirmation'),
    # In urls.py

    path('test/', TestView.as_view(), name='test'),








  



   
   


   


    

 
]