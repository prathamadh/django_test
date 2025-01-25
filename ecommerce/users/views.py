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
from .models import Cart, Order,  OrderItem,Address
from django.utils.decorators import method_decorator

from .recommendation import get_recommendations,recommend_products
from surprise import  SVD
import joblib
model = SVD()
model = joblib.load('lightfm_model.pkl')


# Create your views here.
def index(request):
    categories = Category.objects.all() 
    products = Product.objects.all().order_by('-id')  # Fetch all products in descending order
    products_by_category = {}  # Dictionary to store products grouped by category
    
    for category in categories:
        # Get up to 6 products for the current category
        products_in_category = Product.objects.filter(category=category)[:6]
        products_by_category[category] = products_in_category
    
    if request.user.is_authenticated:
        user_id = request.user.id
        product_list = products.values_list('id', flat=True)
        top_recommended_items = get_recommendations(user_id, model, product_list)
        recommended_products = Product.objects.filter(id__in=top_recommended_items)
        idi=recommend_products("User_2")
        int_id = [int(i) for i in idi]
        user_recommendeded_products = Product.objects.filter(id__in=int_id)


        context = {
            'products': products,
            'categories': categories,
            'products_by_category': products_by_category,
            'recommended': recommended_products,
            'user_recommendeded_products' : user_recommendeded_products,
        }
        return render(request, 'users/reccindex.html', context)
    else:
        context = {
            'products': products,
            'categories': categories,
            'products_by_category': products_by_category,
            
        }
        
    return render(request, 'users/index.html', context)


@login_required
def profile(request):
    addresses = Address.objects.filter(user=request.user)
    orders = Order.objects.filter(user=request.user)
    return render(request, 'users/profile.html', {'addresses':addresses, 'orders':orders})


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
from .models import Product, Wishlist

@login_required
def add_to_wishlist(request, product_id):
    user = request.user
    product = get_object_or_404(Product, id=product_id)
    check_items_presence = Wishlist.objects.filter(user=user, product=product)
    if check_items_presence:
        messages.error(request, 'Product is already in your wishlist.')
        return redirect('/productlist')
    else:
        wishlist = Wishlist.objects.create(product=product, user=user)
        if wishlist:
            messages.success(request, 'Product added to your wishlist successfully.')
            return redirect('/wishlist')
        else:
            messages.error(request, 'Something went wrong.')
            return redirect('/productlist')

@login_required
def show_wishlist_items(request):
    items = Wishlist.objects.filter(user=request.user)
    context = {
        'items': items,
    }
    return render(request, 'users/wishlist.html', context)

@login_required
def remove_wishlist_item(request, wishlist_id):
    item = get_object_or_404(Wishlist, id=wishlist_id)
    item.delete()
    messages.success(request, 'Item removed from your wishlist successfully.')
    return redirect('/wishlist')





from django.urls import reverse
from django.http import HttpResponseRedirect
@login_required
def checkout(request):
    # Get user's cart items
    user_cart_items = Cart.objects.filter(user=request.user)
    
    # Check if the cart is empty before proceeding
    if not user_cart_items.exists():
        messages.add_message(request, messages.ERROR, 'Your cart is empty.')
        return redirect('/cart/')  # Redirect to the cart page if empty
    
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

        # Validate if payment method is selected
        if not payment_method:
            messages.error(request, 'Please select a payment method.')
            return redirect('/checkout/')

        # Create the order
        order = Order.objects.create(
            user=request.user,
            total_price=total_price,
            payment_method=payment_method,
            contact_no=contact_no,
            address=address,
            payment_status=True  # Initially, the payment status is set to False (pending).
        )

        # Create order items
        for item in user_cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                total_price=item.product.product_price * item.quantity
            )

        # Optionally clear the cart after placing the order
        user_cart_items.delete()

        # Handle payment method-specific logic
        if order.payment_method == 'Cash on Delivery':
            messages.add_message(request, messages.SUCCESS, 'Order successfully placed.')
            return redirect('/myorder')  # Redirect to the 'myorder' page where orders are listed

        elif order.payment_method == 'Esewa':
            order_id = order.id
            url = "http://127.0.0.1:8000/esewaform"  # Get the base URL for the 'esewaform' view
            return redirect(f'{url}?o_id={order_id}')  # Pass the order ID to the Esewa payment page

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

@method_decorator(login_required, name='dispatch')
class EsewapaymentView(View):
    def get(self,request,*args,**kwargs):
        o_id=request.GET.get('o_id')
        # c_id=request.GET.get('c_id')
        cart=Cart.objects.filter(user=request.user)
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
            # 'amount':order.product.product_price,
            'amount':order.total_price,
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
def esewa_verify(request):
    if request.method == "GET":
        data = request.GET.get('data')
        order_id = request.GET.get('order_id')
        decoded_data = base64.b64decode(data).decode()
        map_data = json.loads(decoded_data)
        
        try:
            order = Order.objects.get(id=order_id)
            cart = Cart.objects.filter(user=request.user)
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
        
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from .forms import CustomUserChangeForm, CustomPasswordChangeForm

@login_required
def user_profile(request):
    if request.method == 'POST':
        user_form = CustomUserChangeForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('users:profile')
    else:
        user_form = CustomUserChangeForm(instance=request.user)

    return render(request, 'users/profile.html', {'user_form': user_form})

# View to change the password
@login_required
def change_password(request):
    if request.method == 'POST':
        password_form = CustomPasswordChangeForm(request.user, request.POST)
        if password_form.is_valid():
            password_form.save()
            update_session_auth_hash(request, password_form.user)  # To avoid logging out after password change
            messages.success(request, "Your password has been updated successfully.")
            return redirect('users:profile')
    else:
        password_form = CustomPasswordChangeForm(request.user)

    return render(request, 'users/change_password.html', {'password_form': password_form})

# View to handle account deletion
@login_required
def delete_account(request):
    user = request.user
    if request.method == 'POST':
        user.delete()
        messages.success(request, "Your account has been deleted successfully.")
        return redirect('home')  # Redirect to homepage after deletion
    return render(request, 'users/delete_account.html')  # Confirmation page before deletion


class TestView(View):
    def get(self, request):
        return HttpResponse('This is a test view')

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














