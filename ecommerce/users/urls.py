from django.urls import path
from .views import *
urlpatterns=[
    path('',index),
    path('productlist',products),
    path('productdetails/<int:product_id>',productdetails),
    path('addtocart/<int:product_id>',add_to_cart),
    path('cart/',show_cart_items),
    path('removecart/<int:cart_id>',remove_cart_item),
    path('orderform/<int:product_id>/<int:cart_id>',order_form),
    path('esewaform/',EsewaView.as_view(),name='esewaform'),
    path('esewaverify/<int:order_id>/<int:cart_id>',esewa_verify),
    path('myorder/',my_order),
    

 
]