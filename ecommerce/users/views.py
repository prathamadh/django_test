from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.db.models import Sum, F
import hmac
import hashlib
import uuid
import base64
import json
import requests

from products.models import Product
from .models import Cart, Order, Membership, OrderItem
from .forms import OrderForm
from django.views import View


# Create your views here.

def index(request):
    products = Product.objects.all().order_by('-id')[:8]  # Show latest 8 products
    context = {
        'products': products
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

@login_required
def add_to_cart(request, product_id):
    user = request.user
    product = Product.objects.get(id=product_id)
    
    # Check if the product is already in the cart for the user
    check_items_presence = Cart.objects.filter(user=user, product=product)

    if check_items_presence.exists():
        messages.error(request, 'Product is already in the cart.')
        return redirect('/productlist')
    else:
        # Add product to the cart if it's not already there
        cart = Cart.objects.create(product=product, user=user)
        
        if cart:
            messages.success(request, 'Product added to the cart successfully.')
            
            # Get the number of items in the user's cart
            cart_item_count = Cart.objects.filter(user=user).count()
            
            # Optionally, return a JSON response with the updated cart item count
            if request.is_ajax():
                return JsonResponse({'item_count': cart_item_count})
            
            return redirect('/cart')
        else:
            messages.error(request, 'Something went wrong.')
            return redirect('/productlist')
# def add_to_cart(request, product_id):
#     user = request.user
#     product = Product.objects.get(id=product_id)
#     check_items_presence = Cart.objects.filter(user=user, product=product)

#     if check_items_presence:
#         messages.error(request, 'Product is already in the cart.')
#         return redirect('/productlist')
#     else:
#         cart = Cart.objects.create(product=product, user=user)
#         if cart:
#             messages.success(request, 'Product added to the cart successfully.')
#             return redirect('/cart')
#         else:
#             messages.error(request, 'Something went wrong.')
#             return redirect('/productlist')

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
    
    total_price = sum(item.product.product_price * item.quantity for item in user_cart_items)

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
        address = request.POST['address']
        contact_no = request.POST['contact_no']
        payment_method = request.POST['payment_method']

        # Create the order first
        order = Order.objects.create(
            user=request.user,
            total_price=total_price,
            payment_method=payment_method,
            contact_no=contact_no,
            address=address,
            payment_status=False  # Initially, the payment status is set to False (pending).
        )

        # Create Order Items
        for item in user_cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                total_price=item.product.product_price * item.quantity
            )

        # Delete items from cart after the order is created
        user_cart_items.delete()

        # Redirect to respective payment gateway based on selected payment method
        if payment_method == 'Esewa':
            # Redirect to the Esewa payment form
            return redirect(reverse('esewaform') + f"?o_id={order.id}&c_id={order.id}")

        elif payment_method == 'Khalti':
            # Redirect to the Khalti payment form
            return redirect(reverse('khaltiform') + f"?o_id={order.id}&c_id={order.id}")

        messages.success(request, 'Order placed successfully. Please complete the payment.')
        return redirect('order_confirmation')  # You can redirect to a success page here after payment

    return render(request, 'users/checkout.html', {'order_items': order_items, 'total_price': total_price})




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


def order_form(request, product_id, cart_id):
    # Fetch the product and cart details
    product = Product.objects.get(id=product_id)
    cart_item = Cart.objects.get(id=cart_id)
    total_price = cart_item.product.product_price * cart_item.quantity

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Retrieve data from the form
            address = form.cleaned_data['address']
            contact_no = form.cleaned_data['contact_no']
            payment_method = form.cleaned_data['payment_method']

            # Create the order
            order = Order.objects.create(
                user=request.user,
                total_price=total_price,
                payment_method=payment_method,
                contact_no=contact_no,
                address=address,
                payment_status=False  # Initially set to False (pending)
            )

            # Create an order item for this product
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                total_price=total_price
            )

            # Delete the cart item after the order is created
            cart_item.delete()

            # Redirect to the eSewa payment form if payment method is 'Esewa'
            if payment_method == 'Esewa':
                esewa_url = reverse('esewaform') + f"?o_id={order.id}"
                return redirect(esewa_url)

            # For Cash on Delivery
            elif payment_method == 'Cash on Delivery':
                messages.success(request, 'Order placed successfully. Please pay on delivery.')
                return redirect('/myorder')  # Redirect to the order summary page

            else:
                messages.error(request, 'Invalid payment method selected.')
                return render(request, 'users/orderform.html', {'form': form})

        else:
            messages.error(request, 'Please correct the errors in the form.')

    else:
        form = OrderForm()

    # Context for the template
    context = {
        'form': form,
        'product': product,
        'quantity': cart_item.quantity,
        'unit_price': product.product_price,
        'total_price': total_price,
    }
    return render(request, 'users/orderform.html', context)


# @login_required
# def process_order(request, order_id):
#     order = Order.objects.get(id=order_id)
#     user_membership = Membership.objects.get(user=request.user)

#     user_membership.total_purchase_amount += order.total_price
#     user_membership.save()

#     if user_membership.total_purchase_amount >= 20000:
#         user_membership.membership_type = 'Higher'
#     elif user_membership.total_purchase_amount >= 10000:
#         user_membership.membership_type = 'Secondary'
#     elif user_membership.total_purchase_amount >= 5000:
#         user_membership.membership_type = 'Primary'
#     else:
#         user_membership.membership_type = 'General'

#     user_membership.save()
#     return render(request, 'myorder.html', {'order': order})




class EsewaView(View):
    def get(self,request,*args,**kwargs):
        o_id=request.GET.get('o_id')
        c_id=request.GET.get('c_id')
        cart=Cart.objects.get(id=c_id)
        order=Order.objects.get(id=o_id)

        uuid_val=uuid.uuid4()

        def genSha256(key,message):
            key=key.encode('utf-8')
            message=message.encode('utf-8')
            hmac_sha256=hmac.new(key,message,hashlib.sha256)

            digest=hmac_sha256.digest()

            signature=base64.b64encode(digest).decode('utf-8')
            return signature
        
        secret_key='8gBm/:&EnhH.1/q'
        data_to_assign=f"total_amount={order.total_price},transaction_uuid={uuid_val},product_code=EPAYTEST"

        result=genSha256(secret_key,data_to_assign)

        data={
            'amount':order.product.product_price,
            'total_amount':order.total_price,
            'transaction_uuid':uuid_val,
            'product_code':'EPAYTEST',
            'signature':result
        }
        context={
            'order':order,
            'data':data,
            'cart':cart
        }
        return render(request,'users/esewaform.html',context)
    

import json
@login_required
def esewa_verify(request,order_id,cart_id):
    if request.method=="GET":
        data=request.GET.get('data')
        decoded_data=base64.b64decode(data).decode()
        map_data=json.loads(decoded_data)
        order=Order.objects.get(id=order_id)
        cart=Cart.objects.get(id=cart_id)

        if map_data.get('status')=='COMPLETE':
            order.payment_status=True
            order.save()
            cart.delete()
            messages.add_message(request,messages.SUCCESS,'Payment successful.')
            return redirect('/myorder')
        
        else:
            messages.add_message(request,messages.ERROR,'Failed to make payment')
            return redirect('/myorder')


 
# class EsewaView(View):
#     def get(self,request,*args,**kwargs):
#         o_id=request.GET.get('o_id')
#         c_id=request.GET.get('c_id')
#         # cart=Cart.objects.get(id=c_id)
#         try:
#             cart = Cart.objects.get(product_id=o_id, user_id=c_id)

#         except Cart.DoesNotExist:
#             return HttpResponse("Cart not found")



#         order=Order.objects.get(id=o_id)

#         uuid_val=uuid.uuid4()

#         def genSha256(key,message):
#             key=key.encode('utf-8')
#             message=message.encode('utf-8')
#             hmac_sha256=hmac.new(key,message,hashlib.sha256)

#             digest=hmac_sha256.digest()

#             signature=base64.b64encode(digest).decode('utf-8')
#             return signature
        
#         secret_key='8gBm/:&EnhH.1/q'
#         data_to_assign=f"total_amount={order.total_price},transaction_uuid={uuid_val},product_code=EPAYTEST"

#         result=genSha256(secret_key,data_to_assign)

#         data={
#             'amount':order.product.product_price,
#             'total_amount':order.total_price,
#             'transaction_uuid':uuid_val,
#             'product_code':'EPAYTEST',
#             'signature':result
#         }
#         context={
#             'order':order,
#             'data':data,
#             'cart':cart
#         }
#         return render(request,'users/esewaform.html',context)
    

# import json
# @login_required
# def esewa_verify(request,order_id,cart_id):
#     if request.method=="GET":
#         data=request.GET.get('data')
#         decoded_data=base64.b64decode(data).decode()
#         map_data=json.loads(decoded_data)
#         order=Order.objects.get(id=order_id)
#         cart=Cart.objects.get(id=cart_id)

#         if map_data.get('status')=='COMPLETE':
#             order.payment_status=True
#             order.save()
#             cart.delete()
#             messages.add_message(request,messages.SUCCESS,'Payment successful.')
#             return redirect('/myorder')
        
#         else:
#             messages.add_message(request,messages.ERROR,'Failed to make payment')
#             return redirect('/myorder')



   
@login_required
def my_order(request):
    user=request.user
    items=Order.objects.filter(user=user)
    context={
        'items':items
    }
    return render(request,'users/myorder.html',context)













