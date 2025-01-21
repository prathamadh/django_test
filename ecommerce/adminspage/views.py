from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from users.auth import admin_only
from users.models import Order


# Create your views here.
@login_required
@admin_only
def dashboard(request):
    # total_users = User.objects.count()
    # deactivated_users = User.objects.filter(is_active=False).count()
    return render(request, 'admins/dashboard.html', )




@login_required
@admin_only
def order(request):
    # Fetch all orders with their related items
    orders = Order.objects.prefetch_related('items').all()

    # Pass the data to the template
    context = {
        'orders': orders,
    }
    return render(request, 'admins/order.html', context)

# def order(request):
#     items=Order.objects.all()
#     context={
#         'items':items
#     }
#     return render(request,'admins/order.html',context)


from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.utils.timezone import now
@login_required
@admin_only


def show_logged_in_users(request):
    # Get all active users (You can add conditions to only get logged-in users)
    logged_in_users = User.objects.all()

    # Pass the users list to the template
    return render(request, 'admins/users1.html', {'logged_in_users': logged_in_users})

