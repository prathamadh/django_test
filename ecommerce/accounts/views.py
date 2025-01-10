from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import LoginForm


# Register User View
def register_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, 'Account Created.')
            return redirect('/register')  # Redirect after successful registration
        else:
            messages.add_message(request, messages.ERROR, 'Failed to create account.')
            return render(request, 'accounts/register.html', {'form': form})
    
    # For GET requests, render a blank form
    context = {
        'form': UserCreationForm()
    }
    return render(request, 'accounts/register.html', context)


# Login User View
def login_form(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = authenticate(request, username=data['username'], password=data['password'])
            if user is not None:
                login(request, user)
                # Check if the user is a staff member
                if user.is_staff:  
                    return redirect('/admins/dashboard')  # Redirect for staff users
                else:
                    return redirect("/")  # Redirect for regular users
            else:
                messages.add_message(request, messages.ERROR, 'Please provide valid credentials.')
        else:
            messages.add_message(request, messages.ERROR, 'Invalid form submission.')
    else:
        form = LoginForm()  # Initialize blank form for GET requests

    # Pass the form to the context for rendering
    context = {
        'form': form
    }
    return render(request, 'accounts/login.html', context)


# Logout User View
def logout_user(request):
    logout(request)
    messages.add_message(request, messages.INFO, 'You have been logged out.')
    return redirect('/login')  # Redirect to login page
