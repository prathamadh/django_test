

from django.urls import path
from .views import *

# Add the app_name declaration for namespacing
app_name = 'products'

urlpatterns = [
    path('', index, name='index'),
    path('addproduct/', post_product, name='addproduct'),
    path('updateproduct/<int:product_id>/', update_product, name='updateproduct'),
    path('deleteproducts/<int:product_id>/', delete_product, name='deleteproduct'),
    path('addcategory/', post_category, name='addcategory'),
    path('categories/', show_category, name='categories'),
    path('updatecategory/<int:category_id>/', update_category, name='updatecategory'),
    path('deletecategory/<int:category_id>/', delete_category, name='deletecategory'),
    path('search/', search_products, name='search_products'),
]
