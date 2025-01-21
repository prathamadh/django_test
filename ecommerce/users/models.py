from django.db import models
from products.models import Product
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db.models import Sum


# Extend User model to include cart item count
def get_cart_item_count(self):
    return self.cart_set.aggregate(total_items=Sum('quantity'))['total_items'] or 0

User.add_to_class('cart_item_count', property(get_cart_item_count))
# Cart Model (Unchanged)
class Cart(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)  
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.product_name} - {self.quantity}"
 

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlists')
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Wishlist item for {self.user.username} - {self.product.name}"

    class Meta:
        unique_together = ('user', 'product')  # Ensure a user can't add the same product more than once


class Order(models.Model):
    PAYMENT = (
        ('Cash on delivery', 'Cash on delivery'),
        ('Esewa', 'Esewa'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=100, choices=PAYMENT)
    is_paid = models.BooleanField(default=False)
    payment_status = models.BooleanField(default=False, null=True)  # Completed = True, Pending = False
    payment_reference = models.CharField(max_length=255, null=True, blank=True)
    contact_no = models.CharField(max_length=10)
    address = models.CharField(max_length=200)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username} - {self.payment_method}"
from django.db import models
from users.models import Order  # Assuming Order is in the 'users' app
from products.models import Product  # Assuming Product is in the 'products' app

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_ordered = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Automatically calculate the total price if not provided
        if not self.total_price:
            self.total_price = self.quantity * self.product.product_price
        super(OrderItem, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.product_name} (x{self.quantity}) - ${self.total_price}"

# class OrderItem(models.Model):
#     order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     quantity = models.IntegerField()
#     total_price = models.DecimalField(max_digits=10, decimal_places=2)
#     is_ordered = models.BooleanField(default=False)

# Membership Model (Unchanged)
class Membership(models.Model):
    membership_choices = [
        ('General', 'General'),
        ('Primary', 'Primary'),
        ('Secondary', 'Secondary'),
        ('Higher', 'Higher')
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    membership_type = models.CharField(
        max_length=10, choices=membership_choices, default='General'
    )
    total_purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.user.username} - {self.membership_type}"
