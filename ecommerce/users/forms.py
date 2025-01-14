from django.forms import ModelForm
from .models import Order,OrderItem
from django import forms

class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = ['contact_no', 'address', 'payment_method']

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']