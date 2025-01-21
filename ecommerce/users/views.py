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
# from .recommendation import get_recommendations
# from surprise import  SVD
# import joblib
# model = SVD()
# model = joblib.load('lightfm_model.pkl')
# def index(request):
    
#     if request.user.is_authenticated:
#         categories = Category.objects.all() 
#         user_id = request.user.id
#         products = Product.objects.all().order_by('-id')
#         product_list = products.values_list('id', flat=True)
#         recommended_items = get_recommendations(user_id, model,product_list)
#         recommended_products = Product.objects.filter(id__in=recommended_items)
#         context = {
#         'products': products,
#         'categories': categories,
#         'recommended': recommended_products,
#          }

#         return render(request, 'users/reccindex.html', context)
#     else :
#         products = Product.objects.all().order_by('-id') 
#         categories = Category.objects.all()  
#         context={
#         'products': products,
#         'categories': categories  
#         }
#     return render(request, 'users/index.html', context)


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


def show_category(request, category_id=None):
    # Fetch all categories
    categories = Category.objects.all()
    
    # If category_id is passed, filter products based on the category
    if category_id:
        category = get_object_or_404(Category, id=category_id)
        products = Product.objects.filter(category=category)
    else:
        # If no category is selected, show all products
        products = Product.objects.all()

    context = {
        'categories': categories,  # Pass all categories to the template
        'products': products,     # Pass filtered products based on the selected category
    }
    
    return render(request, 'users/category_product.html', context)


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
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Wishlist, Product

@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if created:
        messages.success(request, 'Product added to wishlist.')
    else:
        messages.info(request, 'Product is already in your wishlist.')
    return redirect('wishlist')

@login_required
def remove_from_wishlist(request, item_id):
    wishlist_item = get_object_or_404(Wishlist, id=item_id, user=request.user)
    wishlist_item.delete()
    messages.success(request, 'Product removed from wishlist.')
    return redirect('wishlist')




from django.urls import reverse
from django.http import HttpResponseRedirect
@login_required
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

        # Determine payment status
        if payment_method == 'Cash on Delivery':
            payment_status = "Pending"
            is_paid = False  # For COD, payment status is not paid
        elif payment_method == 'Esewa':
            payment_status = "Payment through Esewa"
            is_paid = True  # For Esewa, payment is processed
        else:
            payment_status = "Failed"
            is_paid = False

        # Create the order
        order = Order.objects.create(
            user=request.user,
            total_price=total_price,
            payment_method=payment_method,
            is_paid=is_paid,
            contact_no=contact_no,
            address=address,
            payment_status=payment_status,  # Set payment status here
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
            # Set payment status to 'True' for Cash on Delivery orders
            order.payment_status = "Paid on Delivery"
            order.save()  # Save the order with updated payment status
            messages.add_message(request, messages.SUCCESS, 'Your order is confirmed. It will be delivered soon.')
            return redirect('/myorder')  # Redirect to the 'My Orders' page (or wherever you'd like)

        elif order.payment_method == 'Esewa':
            # Set payment status to "Payment through Esewa"
            order.payment_status = "Payment through Esewa"
            order.save()  # Save the order with updated payment status
            messages.add_message(request, messages.SUCCESS, 'Your order is being processed through Esewa.')
            return redirect(reverse('esewaform') + "?o_id=" + str(order.id))  # Redirect to the Esewa payment page

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

        # Make sure these values are passed to the template
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
        if not data:
            messages.error(request, 'Invalid response from Esewa.')
            return redirect('/myorder')
        
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

        # Ensure correct response handling
        if map_data.get('status') == 'COMPLETE':
            order.payment_status = True
            order.save()
            cart.delete()  # Delete cart after successful payment
            messages.success(request, 'Payment successful.')
            return redirect('/myorder')
        else:
            messages.error(request, 'Payment failed or was cancelled.')
            return redirect('/myorder')



@login_required
def my_order(request):
    user = request.user
    orders = Order.objects.filter(user=user)
    
    # Get all order items associated with the user's orders
    order_items = OrderItem.objects.filter(order__in=orders)
    
    context = {
        'order_items': order_items  # Pass order items to the template
    }
    
    return render(request, 'users/myorder.html', context)














