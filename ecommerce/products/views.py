from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from .models import Product,Category
from .forms import ProductForm,CategoryForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from users.auth import admin_only
# Create your views here.

@login_required
@admin_only

def index(request):
    #fetch data from the table
    products=Product.objects.all()
    context={
        'products':products
    }
    return render(request,'products/products.html',context)

@login_required
@admin_only
def post_product(request):

    if request.method=="POST":
        form=ProductForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            messages.add_message(request,messages.SUCCESS,'Product added.')
            # return redirect('products/addproduct')
            return redirect('products:addproduct')

        else:
            messages.add_message(request,messages.ERROR,'failed to add product.')
            return render(request,'products/addproduct.html',{'form':form})
        

    context={
        'form':ProductForm
    }

    return render(request,'products/addproduct.html',context)

@login_required
@admin_only
def update_product(request,product_id):
    instance = Product.objects.get(id=product_id)

    if request.method=="POST":
        form = ProductForm(request.POST,request.FILES,instance=instance)
        if form.is_valid():
            form.save()
            messages.add_message(request,messages.SUCCESS,'Product update.')
            return redirect("/products")
        else:
            messages.add_message(request,messages.ERROR,'Failed to update product.')
            return render(request,'/products/updateproduct.html',{'form':form})
    
    
    context={
        'form':ProductForm(instance=instance)
    }
    return render(request,'products/updateproduct.html',context)

@login_required
@admin_only
def delete_product(request,product_id):
    product = Product.objects.get(id=product_id)
    product.delete()
    messages.add_message(request,messages.SUCCESS,'Product deleted')
    return redirect('/products')



@login_required
@admin_only
def post_category(request):

    if request.method=="POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request,messages.SUCCESS,'Category added.')
            return redirect("/products/addcategory")
        else:
            messages.add_message(request,messages.ERROR,'Failed to add catgeory.')
            return render(request,'products/addcategory.html',{'form':form})
    
    
    context={
        'form':CategoryForm
    }
    return render(request,'products/addcategory.html',context)




@login_required

 


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
    
    return render(request, 'products/category_product.html', context)


    




@login_required
@admin_only
def update_category(request,category_id):
    instance = Category.objects.get(id=category_id)

    if request.method=="POST":
        form = CategoryForm(request.POST,instance=instance)
        if form.is_valid():
            form.save()
            messages.add_message(request,messages.SUCCESS,'Catgeory update.')
            return redirect("/products/categories")
        else:
            messages.add_message(request,messages.ERROR,'Failed to update category .')
            return render(request,'/products/updatecategory.html',{'form':form})
    
    
    context={
        'form':CategoryForm(instance=instance)
    }
    return render(request,'products/updatecategory.html',context)


@login_required
@admin_only
def delete_category(request,category_id):
    category= Category.objects.get(id=category_id)
    category.delete()
    messages.add_message(request,messages.SUCCESS,' Category deleted')
    return redirect('/products/categories')




def search_products(request):
    # Get the search query from the request (from the input field named 'q')
    query = request.GET.get('q', '')  # If no query, it will default to an empty string
    if query:  # If the query is not empty
        # Search products whose names contain the query (case-insensitive)
        products = Product.objects.filter(product_name__icontains=query)
    else:
        # If no query, return an empty queryset
        products = Product.objects.none()
    # Render the search results template with the products and query context
    return render(request, 'products/search_result.html', {'products': products, 'query': query})
