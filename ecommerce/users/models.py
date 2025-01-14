from django.db import models
from products.models import Product
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, MaxLengthValidator

# Cart Model (Unchanged)
class Cart(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)  
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.product_name} - {self.quantity}"

class Order(models.Model):
    PAYMENT = (
        ('Cash on delivery', 'Cash on delivery'),
        ('Esewa', 'Esewa')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=100, choices=PAYMENT)
    payment_status = models.BooleanField(default=False, null=True)
    contact_no = models.CharField(max_length=10)
    address = models.CharField(max_length=200)
    created_date = models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_ordered = models.BooleanField(default=False)

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
