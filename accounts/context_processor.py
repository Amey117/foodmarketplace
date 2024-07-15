from vendor.models import Vendor
from . models import UserProfile
def vendor_context_data(request):
    context = {}
    if request.user.is_authenticated and request.user.role==1:
        vendor = Vendor.objects.get(user=request.user)
        context['vendor']=vendor
    return context

def user_profile_context_data(request):
    context={}
    if request.user.is_authenticated:
        user_profile=UserProfile.objects.get(user=request.user)
        context['user_profile']=user_profile
    return context