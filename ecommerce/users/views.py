from django.shortcuts import render,redirect
from products.models import *
from django.contrib.auth.decorators import login_required
from .models import Cart,Order,Membership
from .forms import OrderForm
from django.contrib import messages
from django.urls import reverse
from django.views import View
# Create your views here.
def index(request):
    products=Product.objects.all().order_by('-id')[:8] #jun last ma enter garyo tyo last ma aaune
    context={
        'products':products
    }
    return render(request,'users/index.html',context)

def products(request):
    products=Product.objects.all()
    context={
        'products':products
    }
    return render(request,'users/products.html',context)

def productdetails(request,product_id):
    product=Product.objects.get(id=product_id)
    context={
        'product':product
    }
    return render(request,'users/productdetails.html',context)

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
    user=request.user
    items=Cart.objects.filter(user=user)

    context={
        'items':items
    }
    return render(request,'users/cart.html',context)

@login_required
def remove_cart_item(request,cart_id):
    item=Cart.objects.get(id=cart_id)
    item.delete()
    messages.add_message(request,messages.SUCCESS,"Item removed from the cart successfully")
    return redirect('/cart')

@login_required
def order_form(request,product_id,cart_id):
    user=request.user
    product=Product.objects.get(id=product_id)
    cart_items=Cart.objects.get(id=cart_id)

    if request.method=="POST":
        form=OrderForm(request.POST)
        if form.is_valid():
            quantity=request.POST.get('quantity')
            price=product.product_price
            total_price=int(quantity)*int(price)
            contact_no=request.POST.get('contact_no')
            address=request.POST.get('address')
            payment_method=request.POST.get('payment_method')
            payment_status=request.POST.get('payment_status')

            order=Order.objects.create(
                product=product,
                user=user,
                quantity=quantity,
                total_price=total_price,
                contact_no=contact_no,
                address=address,
                payment_method=payment_method,
                payment_status=payment_status
            )
            if order.payment_method=='Cash on Delivery':
                cart_items.delete()
                messages.add_message(request,messages.SUCCESS,'Order successfully placed.')
                return redirect('/myorder')
            
            elif order.payment_method=='Esewa':
                return redirect(reverse('esewaform')+"?o_id="+str(order.id)+"&c_id="+str(cart_items.id))
            
            else:
                messages.add_message(request,messages.ERROR,'Failed to place and order')
                return render(request,'users/orderform.html',{'form':form})


    context={
        'form':OrderForm
    }
    return render(request,'users/orderform.html',context)
 

def process_order(request, order_id):
    order = Order.objects.get(id=order_id)
    user_membership = Membership.objects.get(user=request.user)
    
    # Add the order total to the user's total purchase amount
    user_membership.total_purchase_amount += order.total_amount
    user_membership.save()

    # Update membership type based on total purchase amount
    if user_membership.total_purchase_amount >= 20000:
        user_membership.membership_type = 'Higher'
    elif user_membership.total_purchase_amount >= 10000:
        user_membership.membership_type = 'Secondary'
    elif user_membership.total_purchase_amount >= 5000:
        user_membership.membership_type = 'Primary'
    else:
        user_membership.membership_type = 'General'

    user_membership.save()

    # Return some confirmation response
    return render(request, 'myorder.html', {'order': order})


import hmac
import hashlib
import uuid #to generate random string
import base64

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

@login_required
def my_order(request):
    user=request.user
    items=Order.objects.filter(user=user)
    context={
        'items':items
    }
    return render(request,'users/myorder.html',context)
    




