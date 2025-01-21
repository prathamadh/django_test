from django.contrib import admin
from .models import Order, OrderItem
# Register your models here.
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Display the columns for the Order model in the admin panel
    list_display = ('id', 'user', 'total_price', 'payment_status', 'created_date')
    # Allow filtering orders by payment status and creation date
    list_filter = ('payment_status', 'created_date')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    # Display the columns for the OrderItem model in the admin panel
    list_display = ('order', 'product', 'quantity', 'total_price', 'is_ordered')


from django.contrib import admin
from .models import Wishlist

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_on')
    list_filter = ('added_on',)
    search_fields = ('user__username', 'product__name')
