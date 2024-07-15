from datetime import date,datetime
from django.shortcuts import render, get_object_or_404, HttpResponse,redirect
from django.http import JsonResponse
from django.urls import reverse
from django.db.models import Prefetch
from django.contrib.auth.decorators import login_required
from vendor.models import Vendor
from menu.models import Category, FoodItem
from vendor.models import OpeningHour
from orders.forms import OrderForm
from accounts.models import UserProfile
from .models import Cart
from .context_processors import cart_counter,get_cart_amount

# Create your views here.


def market_place(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    context = {"vendors": vendors}
    return render(request, "market_place/listings.html", context)


def vendor_details(request, vendor_slug):
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)
    vendor_categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch("food_items", queryset=FoodItem.objects.filter(is_available=True))
    )
    opening_hrs = OpeningHour.objects.filter(vendor=vendor).order_by('day','from_hour')
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = []
    
    # todays day
    today = date.today()
    weekday_number = today.weekday() + 1 # it gives 0 for monday
    current_day_opening_hrs = OpeningHour.objects.filter(vendor=vendor,day=weekday_number)
    
    
    print("current_day",weekday_number)
    context = {
        "vendor": vendor,
        "vendor_categories": vendor_categories,
        "cart_items": cart_items,
        "opening_hrs":opening_hrs,
        "current_day_opening_hrs":current_day_opening_hrs
    }
    return render(request, "market_place/listing_details.html", context)


def add_to_cart(request, food_id=None):
    if request.user.is_authenticated:
        try:
            # check if the food item exists
            fooditem = FoodItem.objects.get(id=food_id)
            # check if the user has already added food to the cart
            try:
                check_cart = Cart.objects.get(user=request.user, fooditem=fooditem)
                # already added the food item for that user in his cart
                # increase the quantity
                check_cart.quantity += 1
                check_cart.save()
                return JsonResponse(
                    {
                        "status": "success",
                        "message": "cart quantity increase",
                        "cart_counter": cart_counter(request),
                        "qty_counter": check_cart.quantity,
                        "cart_amount":get_cart_amount(request)
                    }
                )
            except:
                # food item not added for that user in his cart
                Cart.objects.create(user=request.user, fooditem=fooditem, quantity=1)
                return JsonResponse(
                    {
                        "status": "success",
                        "message": "new cart item added",
                        "cart_counter": cart_counter(request),
                        "qty_counter":1,
                        "cart_amount":get_cart_amount(request)
                    }
                )
        except:
            return JsonResponse({"status": "success", "message": "user logged in"})
    else:
        return JsonResponse({"status": "login_required", "message": "please login to continue"})


def decrease_cart(request, food_id=None):
    if request.user.is_authenticated:
        try:
            # check if the food item exists
            fooditem = FoodItem.objects.get(id=food_id)
            # check if the user has already added food to the cart
            try:
                check_cart = Cart.objects.get(user=request.user, fooditem=fooditem)
                # already added the food item for that user in his cart
                # increase the quantity
                check_cart.quantity -= 1
                if check_cart.quantity == 0:
                    # remove entry from the cart table
                    check_cart.delete()
                else:
                    check_cart.save()
                return JsonResponse(
                    {
                        "status": "success",
                        "message": "cart quantity decrease",
                        "cart_counter": cart_counter(request),
                        "qty_counter": check_cart.quantity,
                        "cart_amount":get_cart_amount(request)
                    }
                )
            except:
                # food item not added for that user in his cart so no point in decreasing it
                return JsonResponse(
                    {
                        "status": "fail",
                        "message": "cart item not present to remove",
                        "cart_counter": cart_counter(request),
                        "qty_counter": 0,
                        "cart_amount":get_cart_amount(request)
                    }
                )
        except:
            return JsonResponse({"status": "success", "message": "user logged in"})
    else:
        return JsonResponse({"status": "login_required", "message": "please login to continue"})
    
@login_required(login_url='login')
def cart(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    context={
        "cart_items":cart_items
    }
    return render(request,'market_place/cart.html',context)

def delete_cart(request,cart_id):
    if request.user.is_authenticated:
        try:
            cart_item = Cart.objects.get(id=cart_id)
            cart_item.delete()
            return JsonResponse({"status": "success", "message": "cart item has been deleted ","cart_counter": cart_counter(request),"cart_amount":get_cart_amount(request)})
        except:
            return JsonResponse({"status": "failed", "message": "cart item doesnot exist"})
    else:
        return JsonResponse({"status": "login_required", "message": "please login to continue"})




# checkout views 



def checkout(request):
    user_profile = UserProfile.objects.get(user=request.user)
    default_values = {
        'first_name':request.user.first_name,
        'last_name':request.user.last_name,
        'phone':request.user.phone_number,
        'email':request.user.email,
        'address':user_profile.address,
        'country':user_profile.country,
        'state':user_profile.state,
        'city':user_profile.city,
        'pin_code':user_profile.pin_code
    }
    order_form = OrderForm(initial=default_values)

    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    if cart_items.count()<=0:
        return redirect(reverse('cart'))
    context = {
        'order_form':order_form,
        'cart_items':cart_items
    }
    return render(request,'market_place/checkout.html',context)
