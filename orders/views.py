import json
import razorpay
from django.shortcuts import render
from foodonline.settings import RZP_KEY_SECRET,RZP_KEY_ID
from marketplace.context_processors import get_cart_amount
from marketplace.models import Cart
from .models import Order
from .forms import OrderForm
from .utils import generate_order_no
# Create your views here.

rzp_client = razorpay.Client(auth=(RZP_KEY_ID,RZP_KEY_SECRET))


def place_order(request):
    data_to_save = dict()
    cart_details = get_cart_amount(request)
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    if request.method == 'POST':
        input_data = request.POST
        order_form = OrderForm(data=request.POST)
        if order_form.is_valid():
            data_to_save = order_form.cleaned_data
            data_to_save['user']=request.user
            data_to_save['total'] = cart_details['grand_total']
            data_to_save['tax_data'] = cart_details['taxes_list']
            data_to_save['total_tax'] = cart_details['grand_total'] - cart_details['sub_total']
            data_to_save['payment_method']=input_data['payment_method']
            data_to_save['order_number'] = generate_order_no(request.user.id)
            order=Order.objects.create(**data_to_save)

            # Razor pay payment
            data = {
                "amount":int(data_to_save['total'])*100, # it handles in paise
                "currency":"INR",
                "receipt": "receipt #"+order.order_number,
                "notes": {
                    "key1": "value3",
                    "key2": "value2"
                }
            }
            rzp_order = rzp_client.order.create(data=data)
            #{'amount': 88200, 'amount_due': 88200, 'amount_paid': 0, 'attempts': 0, 'created_at': 1720291345, 'currency': 'INR', 'entity': 'order', 'id': 'order_OVRv4hdayHCXko', 'notes': [], 'offer_id': None, 'receipt': None, 'status': 'created'}
            print("*********************rzp_order",rzp_order)

            print("*****response is order ",order)
        else:
            print("**** form errors",order_form.errors())
    return render(request,'orders/place_order.html',{"order":order,"cart_items":cart_items,"RZP_KEY_ID":RZP_KEY_ID,"rzp_obj":rzp_order})