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
    items=Order.objects.all()
    context={
        'items':items
    }
    return render(request,'admins/order.html',context)
