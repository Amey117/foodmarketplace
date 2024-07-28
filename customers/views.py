from django.shortcuts import render,get_object_or_404,redirect
from accounts.forms import UserProfileForm,UserInfoForm
from accounts.models import UserProfile
from orders.models import Order,OrderedFood
from django.contrib import messages
# Create your views here.


def cprofile(request):
    print("inside c profile ***")
    user_profile_instance = get_object_or_404(UserProfile,user=request.user)
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST,request.FILES,instance=user_profile_instance)
        user_form = UserInfoForm(request.POST,instance=request.user)
        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            messages.success(request,"Profile Data updated")
        else:
            print("error occured",profile_form.errors,user_form.errors)
            messages.error(request,"Failed to update data")
        redirect('cprofile')
    else:
        profile_form = UserProfileForm(instance=user_profile_instance)
        user_form = UserInfoForm(instance=request.user)
    context = {
        'profile_form':profile_form,
        'user_form':user_form,
        'user_profile':user_profile_instance
    }
    return render(request,'customers/cprofile.html',context)


def my_orders(request):
    my_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'orders':my_orders
    }
    return render(request,'customers/myorders.html',context)

def order_details(request,order_number):
    order = Order.objects.get(order_number=order_number)
    ordered_food = OrderedFood.objects.filter(order=order)
    context = {
        'order':order,
        'ordered_food':ordered_food,
        'subtotal':order.total - order.total_tax
    }
    return render(request,'customers/order_detail.html',context)
