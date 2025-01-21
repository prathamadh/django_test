# adminspage/admin.py
from django.contrib import admin
from users.models import OrderItem, Order  # Import only OrderItem from the users app



class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1  # Number of empty forms to display by default







class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ('id', 'customer', 'contact_no', 'address', 'payment_method', 'created_at')
    list_filter = ('payment_method',)
    search_fields = ('customer__username', 'address', 'contact_no')

# admin.site.register(OrderAdmin)
