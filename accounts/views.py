from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from vendor.forms import VendorForm
from .forms import userRegistrationForm
from .models import User, UserProfile
from .utils import detech_user,send_verification_email,send_password_reset_link
from vendor.models import Vendor
from .utils import check_role_customer,check_role_vendor
# Create your views here.




def register_user(request):

    if request.user.is_authenticated:
        messages.warning(request, "Already have an account")
        return redirect("my_account")

    if request.method == "POST":
        print(request.POST)

        form = userRegistrationForm(request.POST)
        if form.is_valid():
            # creating user using create user method
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password,
            )
            user.role = User.CUSTOMER
            user.save()
            # send verification email to the user
            send_verification_email(request,user)
            print("user is saved !!!!!")
            # creating user with form
            # user = form.save(commit=False)
            # user.role = User.CUSTOMER
            # user.save()
            messages.success(request, "Account created successfully,Pls check your mail ")
            return redirect("register_user")
        else:
            print("invalid form !!!, it have some errors")
            print(form.errors)
    else:
        form = userRegistrationForm()
    context = {"form": form}
    return render(request, "accounts/registeruser.html", context)


def register_vendor(request):

    if request.user.is_authenticated:
        messages.warning(request, "Already have an vendor account")
        return redirect("my_account")

    if request.method == "POST":
        form = userRegistrationForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)
        if form.is_valid() and v_form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password,
            )
            user.role = User.RESTAURANT
            user.save()
            vendor = v_form.save(commit=False)
            vendor.user = user
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()
            # send verification email to the user
            send_verification_email(request,user)
            messages.success(
                request,
                "Your account have be created successfully , pls wait for approval",
            )
            return redirect("register_vendor")
        else:
            print(form.errors)
            print(form.errors)
    else:
        form = userRegistrationForm()
        v_form = VendorForm()
    context = {"form": form, "v_form": v_form}
    return render(request, "accounts/registervendor.html", context)


def login(request):
    if request.user.is_authenticated:
        messages.warning(request, "Already logged in")
        return redirect("my_account")

    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = auth.authenticate(email=email, password=password)
        if user is not None:
            auth.login(request, user)
            #messages.success(request, "You have logged in ")
            return redirect("my_account")
        else:
            messages.error(request, "invalid credential")
            return redirect("login")
    else:
        print("invalid email or password !")
        return render(request, "accounts/login.html")


def logout(request):
    auth.logout(request)
    messages.info(request, "You are logged off")
    return redirect("login")


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def vendor_dashboard(request):
    vendor = Vendor.objects.get(user=request.user)
    if vendor.is_approved:
        return render(request, "accounts/vendor_dashboard.html")
    else:
        auth.logout(request)
        messages.info(request, "You Need to wait for approval form our admins")
        return render(request, "accounts/login.html")



@login_required(login_url="login")
@user_passes_test(check_role_customer)
def customer_dashboard(request):
    return render(request, "accounts/customer_dashboard.html")


@login_required(login_url="login")
def my_account(request):
    user = request.user
    redirect_url = detech_user(user)
    return redirect(redirect_url)


def activate(request,uid64,token):
    try:
        user_id = urlsafe_base64_decode(uid64)
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        user = None
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        messages.success(request,'Your account have been activated')
    else:
        messages.error(request,'Invalid token,Account could not be activated')

    return redirect('my_account')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        user = User.objects.get(email=email)
        if user:
            #email is valid we have an account with that email
            user = User.objects.get(pk=user.pk)
            send_password_reset_link(request,user)
            messages.success(request,"Reset password mail send ")
            return redirect('login')
        else:
            messages.error(request,"could not find your account :( ")
    return render(request,'accounts/forgot_password.html')

def reset_password_validate(request,uid64,token):
    #here we will validate the token
    try:
        user_id = int(urlsafe_base64_decode(uid64))
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        user = None
    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid']=user_id
        messages.success(request,'pls reset your password')
        return redirect('reset_password')
    else:
        messages.error(request,'Invalid token,Account could not be activated')

    return redirect('login')

def reset_password(request):
    # here we will reset password
    # extract the password and conf password field
    if request.method == 'POST':
        passwrd = request.POST['password']
        c_passwrd = request.POST['confirm_password']
        if passwrd==c_passwrd:
            user = User.objects.get(pk=request.session['uid'])
            user.set_password(passwrd)
            user.save()
            messages.success(request,"password update successful")
            return redirect('login')
        else:
            messages.error(request,"Confirm password does not match :(")
    return render(request,'accounts/set_new_password.html')

    