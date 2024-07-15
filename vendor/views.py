from django.shortcuts import render, get_object_or_404, redirect,HttpResponse
from django.contrib import messages
from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from accounts.utils import check_role_vendor
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template.defaultfilters import slugify
from django.db import IntegrityError
from django.http import JsonResponse
from django.urls import reverse
from .models import Vendor,OpeningHour
from .forms import VendorForm,OpeningHourForm
from menu.models import Category,FoodItem
from menu.forms import CategoryForm,FoodForm

# Create your views here.

#get vendor from request

def get_vendor(user):
    vendor = Vendor.objects.get(user=user)
    return vendor

def get_category(cat_id):
    category = Category.objects.get(pk=cat_id)
    return category


@login_required()
@user_passes_test(check_role_vendor)
def vendor_profile(request):

    profile = get_object_or_404(UserProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)
    if request.method == "POST":
        user_profile_form = UserProfileForm(
            request.POST, request.FILES, instance=profile
        )
        vendor_profile_form = VendorForm(request.POST, request.FILES, instance=vendor)
        if user_profile_form.is_valid() and vendor_profile_form.is_valid():
            user_profile_form.save()
            vendor_profile_form.save()
            messages.success(request, "Profile updated !")
            return redirect("vendor_profile")
        else:
            print("error occured!")
    else:
        user_profile_form = UserProfileForm(instance=profile)
        vendor_profile_form = VendorForm(instance=vendor)
    context = {
        "user_profile_form": user_profile_form,
        "vendor_profile_form": vendor_profile_form,
    }
    return render(request, "vendor/vendor_profile.html", context)

@login_required()
@user_passes_test(check_role_vendor)
def menu_builder(request):
    categories = Category.objects.filter(vendor__user=request.user).values()
    print("categories",categories)
    return render(request,'vendor/menu_builder.html',{"categories":categories})

@login_required()
@user_passes_test(check_role_vendor)
def fooditems_by_category(request,pk):
    category = get_object_or_404(Category,pk=pk)
    food_items = FoodItem.objects.filter(category=pk,vendor__user=request.user).order_by('created_at')
    print("food_items = > ",food_items)
    return render(request,'vendor/fooditems_by_category.html',{'food_items':food_items,"category":category})

@login_required()
@user_passes_test(check_role_vendor)
def add_category(request):
    if request.method=='POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category_name = form.data['category_name']
            category_obj = form.save(commit=False)
            category_obj.vendor = get_vendor(request.user)
            category_obj.slug = slugify(category_name)
            category_obj.save()
            messages.success(request,"category added successfully")
            return redirect('menu_builder')
        else:
            messages.error(request,"error while adding category")
    else:
        form = CategoryForm()   
    return render(request,"vendor/add_category.html",{"cat_form":form})

@login_required
@user_passes_test(check_role_vendor)
def edit_category(request,pk):
    category = get_object_or_404(Category,pk=pk)
    if request.method=='POST':
        form = CategoryForm(request.POST,instance=category)
        if form.is_valid():
            category_name = form.data['category_name']
            category_obj = form.save(commit=False)
            category_obj.vendor = get_vendor(request.user)
            category_obj.slug = slugify(category_name)
            category_obj.save()
            messages.success(request,"category edited successfully")
            return redirect('menu_builder')
        else:
            messages.error(request,"error while editing category")
    else:
        form = CategoryForm(instance=category)

    return render(request,'vendor/edit_category.html',{"cat_form":form,"cat_id":category.id})

@login_required
@user_passes_test(check_role_vendor)
def delete_category(request,pk=None):
    category = get_object_or_404(Category,pk=pk)
    category.delete()
    messages.success(request,"category deleted successfully")
    return redirect('menu_builder')
    
@login_required
@user_passes_test(check_role_vendor)
def add_food(request):
    if request.method == 'POST':
        form = FoodForm(request.POST,request.FILES)
        if form.is_valid():
            food_obj = form.save(commit=False)
            food_obj.vendor = get_vendor(request.user)
            food_obj.slug = slugify(food_obj.food_title)
            food_obj.save()
            messages.success(request,"food item added successfully")
            return redirect('fooditems_by_category',food_obj.category.id)
        else:
            print(form.errors)
            messages.error(request,"error while adding food item")
    else:
        # this form is empty so we do not knew while creating instance of form which vendor is logged in
        form = FoodForm()
        current_vendor = get_vendor(request.user)
        form.fields['category'].queryset = Category.objects.filter(vendor=current_vendor)
 

            
    return render(request,'vendor/add_food.html',{"food_form":form})


@login_required
@user_passes_test(check_role_vendor)
def edit_food(request,pk=None):
    food_instance = get_object_or_404(FoodItem,pk=pk)
    if request.method=='POST':
        form = FoodForm(request.POST,request.FILES,instance=food_instance)
        if form.is_valid():
            food_obj = form.save(commit=False)
            food_obj.slug = slugify(food_obj.food_title)
            food_obj.vendor = get_vendor(request.user)
            food_obj.save()
            messages.success(request,"food item added successfully")
            return redirect('fooditems_by_category',food_obj.category.id)
        else:
            print("error occured while editing",form.errors)
            messages.error(request,"error while editing food item")
    else:
        form = FoodForm(instance=food_instance)
        current_vendor = get_vendor(request.user)
        form.fields['category'].queryset = Category.objects.filter(vendor=current_vendor)

    return render(request,'vendor/edit_food.html',{'food_form':form,'food_instance':food_instance})


@login_required
@user_passes_test(check_role_vendor)
def delete_food(request,pk=None):
    food_item = get_object_or_404(FoodItem,pk=pk)
    category_id = food_item.category.id
    food_item.delete()
    messages.success(request,"food item deleted successfully")
    return redirect('fooditems_by_category',category_id)


############ OPENING HOURS ###########

@login_required
@user_passes_test(check_role_vendor)
def opening_hours(request):
    opening_hours = OpeningHour.objects.filter(vendor=get_vendor(request.user))
    form = OpeningHourForm()
    context = {
        'form':form,
        'opening_hours':opening_hours
    }
    return render(request,'vendor/opening_hours.html',context)


@login_required
@user_passes_test(check_role_vendor)
def add_opening_hours(request):
    day = request.POST.get('day')
    from_hour = request.POST.get('from_hour')
    to_hour = request.POST.get('to_hour')
    is_closed = request.POST.get('is_closed')
    is_closed_bool = str(is_closed).lower() == 'true'

    try:
        opening_hrs = OpeningHour.objects.create(vendor=get_vendor(request.user),day=day,from_hour=from_hour,to_hour=to_hour,is_closed=is_closed_bool)
        if opening_hours:
            opening_hrs_obj = OpeningHour.objects.get(id=opening_hrs.id)
            remove_url = reverse('remove_opening_hours',args=[opening_hrs_obj.id])
            
            # because after save and retrival mapping is done for choice field labels
            if opening_hrs_obj.is_closed:
                response = {'status':"success",'msg':"opening hrs added successfully",'is_closed':opening_hrs_obj.is_closed,'day':opening_hrs_obj.get_day_display(),'id':opening_hrs_obj.id,'remove_url':remove_url}
            else:
                response = {'status':"success",'msg':"opening hrs added successfully",'day':opening_hrs_obj.get_day_display(),'from_hour':opening_hrs_obj.from_hour,'to_hour':opening_hrs_obj.to_hour,'id':opening_hrs_obj.id,'remove_url':remove_url}
           
        return JsonResponse(response)
    except IntegrityError:
        data = {'status':"error",'msg':f"you have already these hrs"}
        return JsonResponse(data)


@login_required
@user_passes_test(check_role_vendor)
def remove_opening_hours(request,pk=None):
    if request.user.is_authenticated:
        try:
            hour = get_object_or_404(OpeningHour,pk=pk)
            hour.delete()
            response = {'status':'success','id':pk}
            return JsonResponse(response)
        except:
            response = {'status':'error'}
            return JsonResponse(response)
    return HttpResponse("delete opening hrs")
