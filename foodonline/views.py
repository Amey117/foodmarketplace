from django.shortcuts import render
from django.http import HttpResponse
from vendor.models import Vendor
def index(request):
    vendors = Vendor.objects.filter(is_approved=True,user__is_active=True)[:8]
    print("active vendors is ",vendors)
    return render(request,template_name="home.html",context={"vendors":vendors})