from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.messages import get_messages
from django.contrib.auth import update_session_auth_hash

from django.contrib.auth.views import PasswordResetView

from .models import CustomUser
import re
from .forms import ProfileForm
from .models import Profile


def log_in(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        remember_me = request.POST.get("remember_me")
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            
            if remember_me:
                request.session.set_expiry(1209600) 
            else:
                request.session.set_expiry(0)
            
           
            messages.success(request, f"Welcome {user.username}, you are logged in!")
            
           
            next_url = request.POST.get("next")
            if next_url and next_url != "index":
                return redirect(next_url)
            return redirect("index") 
            
        else:
            messages.error(request, "Invalid Username or Password!!!")
            return redirect('log_in')
            
    next_url = request.GET.get("next", "")
    return render(request, 'accounts/login.html', {'next': next_url})

def log_out(request):
   
    storage = get_messages(request)
    for message in storage:
        pass
        
    logout(request)
   
    messages.info(request, "You have been logged out successfully.")
    return redirect("log_in")


def register(request):
    if request.method == 'POST':

        fname = request.POST.get('firstname')
        lname = request.POST.get('lastname')
        uname = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('full_phone')
        address = request.POST.get('street_address')
        pass1 = request.POST.get('password')
        pass2 = request.POST.get('password_confirmation')


        if pass1 != pass2:
            messages.error(request, "Passwords do not match!")
            return redirect('register')

        if CustomUser.objects.filter(username=uname).exists():
            messages.error(request, "Username already taken!")
            return redirect('register')

        user = CustomUser.objects.create_user(
            username=uname,
            email=email,
            password=pass1,
            first_name=fname,
            last_name=lname,
            phone=phone,              
            street_address=address  
        )
        user.save()

        
        messages.success(request, "Registration successful!")
        return redirect('log_in')

    return render(request, 'accounts/register.html')


@login_required(login_url='log_in')
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()

            update_session_auth_hash(request, user) 
            messages.success(request, "Your password was successfully updated!")
            return redirect("index")
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = PasswordChangeForm(user=request.user)
    
    return render(request, 'accounts/password_change.html', {'form': form})

class MyPasswordResetView(PasswordResetView):
    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            messages.error(self.request, "This email is not registered in our system.")
            return self.form_invalid(form)
        return super().form_valid(form)
    

@login_required(login_url='login')    
def profile_dashboard(request):
    return render(request,'profile/dashboard.html')    

@login_required(login_url='login')
def profile(request):
    user_profile, created = Profile.objects.get_or_create(user=request.user)
    form = ProfileForm(instance=user_profile)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')

    context = {
        'form': form,
    }
    return render(request, 'profile/profile.html', context)

from payments.models import Order
@login_required(login_url='login')
def my_order(request):
    orders=Order.objects.filter(user=request.user)
    return render(request,'profile/my_order.html',{'orders':orders})