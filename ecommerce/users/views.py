from django.views import View
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.db.models import Sum, F
import hmac
import hashlib
import uuid
import base64
import requests
from django.shortcuts import redirect, get_object_or_404
from products.models import Product, Category
from .models import Cart, Order,  OrderItem





# Create your views here.


def index(request):
    products = Product.objects.all().order_by('-id') 
    categories = Category.objects.all()  
    context = {
        'products': products,
        'categories': categories  
    }
    return render(request, 'users/index.html', context)



def products(request):
    products = Product.objects.all()
    context = {
        'products': products
    }
    return render(request, 'users/products.html', context)

def productdetails(request, product_id):
    product = Product.objects.get(id=product_id)
    context = {
        'product': product
    }
    return render(request, 'users/productdetails.html', context)




def number_of_items(request):
    # Ensure the user is authenticated
    user = request.user if request.user.is_authenticated else None
    return render(request, 'cart.html', {'user': user}) 

@login_required
def add_to_cart(request,product_id):
    user=request.user
    product=Product.objects.get(id=product_id)
    check_items_presence=Cart.objects.filter(user=user,product=product)
    if(check_items_presence):
        messages.add_message(request,messages.ERROR,'product is already in the cart.')
        return redirect('/productlist')
    else:
        cart=Cart.objects.create(product=product,user=user)
        if cart:
            messages.add_message(request,messages.SUCCESS,'product added to the cart successfully.')
            return redirect('/cart')
        else:
            messages.add_message(request.messages.ERROR,'Something went wrong.')







@login_required
def show_cart_items(request):
    items = Cart.objects.filter(user=request.user)
    for item in items:
        item.total_price = item.product.product_price * item.quantity

    total_bill = items.aggregate(total=Sum(F('quantity') * F('product__product_price')))['total'] or 0

    context = {
        'items': items,
        'total_bill': total_bill,
    }
    return render(request, 'users/cart.html', context)




@login_required
def checkout(request):
    user_cart_items = Cart.objects.filter(user=request.user)
    
    # Calculate the total price of all items in the cart
    total_price = sum(item.product.product_price * item.quantity for item in user_cart_items)

    # Prepare order items summary for display or processing
    order_items = [
        {
            'product': item.product,
            'quantity': item.quantity,
            'unit_price': item.product.product_price,
            'total_price': item.product.product_price * item.quantity
        }
        for item in user_cart_items
    ]

    if request.method == 'POST':
        # Get data from the form
        address = request.POST.get('address')
        contact_no = request.POST.get('contact_no')
        payment_method = request.POST.get('payment_method')

        # Create the order
        order = Order.objects.create(
            user=request.user,
            total_price=total_price,
            payment_method=payment_method,
            contact_no=contact_no,
            address=address,
            payment_status=False  # Initially, the payment status is set to False (pending).
        )

        # Create order items
        for item in user_cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                total_price=item.product.product_price * item.quantity
            )

        # Delete items from the cart after the order is created
        user_cart_items.delete()
        

        # Handle payment method-specific logic
        if order.payment_method == 'Cash on Delivery':
            messages.add_message(request, messages.SUCCESS, 'Order successfully placed.')
            return redirect('/myorder')
        
        elif order.payment_method == 'Esewa':
            # Check if the cart is not empty
            if user_cart_items.exists():
                
                # Redirect to the esewa payment page with order_id and cart_id
                return redirect(reverse('esewaform', args=[order.id, user_cart_items.first().id]))
            else:
                messages.add_message(request, messages.ERROR, 'Cart is empty.')
                return redirect('cart')
        
        else:
            messages.add_message(request, messages.ERROR, 'Failed to place the order.')
            return render(request, 'users/checkout.html', {'order_items': order_items})

    # Handle GET request by rendering the checkout page
    return render(request, 'users/checkout.html', {
        'order_items': order_items,
        'total_price': total_price
    })






@login_required
def order_confirmation(request):
    context = {
        'message': 'Your order has been placed successfully!'
    }
    return render(request, 'users/order_confirmation.html', context)

@login_required
def remove_cart_item(request, cart_id):
    item = Cart.objects.get(id=cart_id)
    item.delete()
    messages.success(request, "Item removed from the cart successfully.")
    return redirect('/cart')

@login_required







class EsewaPaymentView(View):
    def get(self, request, *args, **kwargs):
        o_id = request.GET.get('o_id')
        c_id = request.GET.get('c_id')
        
        try:
            cart = Cart.objects.filter(id=c_id)
            order = Order.objects.get(id=o_id)
        except Cart.DoesNotExist:
            messages.error(request, 'Cart not found.')
            return redirect('cart')
        except Order.DoesNotExist:
            messages.error(request, 'Order not found.')
            return redirect('orders')

        # Calculate total price from the cart items
        total_price = sum(cart_item.product.product_price * cart_item.quantity for cart_item in cart)

        # Generate UUID for the transaction
        uuid_val = uuid.uuid4()

        def genSha256(key, message):
            key = key.encode('utf-8')
            message = message.encode('utf-8')
            hmac_sha256 = hmac.new(key, message, hashlib.sha256)
            digest = hmac_sha256.digest()
            signature = base64.b64encode(digest).decode('utf-8')
            return signature
        
        secret_key = '8gBm/:&EnhH.1/q'
        data_to_assign = f"total_amount={total_price},transaction_uuid={uuid_val},product_code=EPAYTEST"

        result = genSha256(secret_key, data_to_assign)

        data = {
            'amount': total_price,
            'total_amount': total_price,
            'transaction_uuid': uuid_val,
            'product_code': 'EPAYTEST',
            'signature': result
        }

        context = {
            'order': order,
            'data': data,
            'cart': cart
        }

        return render(request, 'users/esewaform.html', context)
import json
@login_required
def esewa_verify(request, order_id, cart_id):
    if request.method == "GET":
        data = request.GET.get('data')
        decoded_data = base64.b64decode(data).decode()
        map_data = json.loads(decoded_data)
        
        try:
            order = Order.objects.get(id=order_id)
            cart = Cart.objects.get(id=cart_id)
        except Order.DoesNotExist:
            messages.error(request, 'Order not found.')
            return redirect('orders')
        except Cart.DoesNotExist:
            messages.error(request, 'Cart not found.')
            return redirect('cart')

        if map_data.get('status') == 'COMPLETE':
            order.payment_status = True
            order.save()
            cart.delete()
            messages.success(request, 'Payment successful.')
            return redirect('/myorder')
        else:
            messages.error(request, 'Failed to make payment')
            return redirect('/myorder')

# In views.py
from django.http import HttpResponse
from django.views import View

class TestView(View):
    def get(self, request):
        return HttpResponse('This is a test view')








 




   
@login_required
def my_order(request):
    user=request.user
    items=Order.objects.filter(user=user)
    context={
        'items':items
    }
    return render(request,'users/myorder.html',context)













