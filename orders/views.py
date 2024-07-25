import json
from django.views import View
import stripe
from django.shortcuts import render,redirect,get_object_or_404
from django.http.response import JsonResponse
from django.http import HttpResponse
from django.conf import settings
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from foodonline.settings import STRIPE_PUBLISHABLE_KEY,STRIPE_SECRET_KEY
from marketplace.context_processors import get_cart_amount
from marketplace.models import Cart
from accounts.models import User
from .models import Order,Payment,OrderedFood
from .forms import OrderForm
from .utils import generate_order_no
# Create your views here.

stripe.api_key = STRIPE_SECRET_KEY


def payment_form(request):
    return render(request, 'orders/payment.html', {'stripe_publishable_key': STRIPE_PUBLISHABLE_KEY})

@csrf_exempt
def create_intent(request):
    print(" ******* inside create payment intent ")
    stripe.api_key = STRIPE_SECRET_KEY
    intent= stripe.PaymentIntent.create(
        amount=177,
        currency='inr',
        description="food online service"
    )
    print("intent is ",intent)
    return JsonResponse({'client_secret':intent.client_secret})

def place_order(request):
    # once checkout is clicked
    # we will make entry in db with the status as initiated
    data_to_save = dict()
    cart_details = get_cart_amount(request)
    print("url for success is ************",request.build_absolute_uri(reverse('payment_success')))
  
    if request.method == 'POST':
        input_data = request.POST
        order_form = OrderForm(data=request.POST)
        if order_form.is_valid():

            payment_object = Payment.objects.create(
                user = request.user,
                amount = cart_details['grand_total'],
                status = 'initiated'
            )

            data_to_save = order_form.cleaned_data
            data_to_save['user']=request.user
            data_to_save['total'] = cart_details['grand_total']
            data_to_save['tax_data'] = cart_details['taxes_list']
            data_to_save['total_tax'] = cart_details['grand_total'] - cart_details['sub_total']
            data_to_save['payment_method']=input_data['payment_method']
            data_to_save['order_number'] = generate_order_no(request.user.id)
            data_to_save['status'] = 'initiated' #initiated
            data_to_save['payment_id'] = payment_object.id
            order=Order.objects.create(**data_to_save)
            

            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                    "price_data": {
                        "currency": "inr",
                        "unit_amount": int(cart_details['grand_total']) * 100,
                        "product_data": {
                            "name": "Food online name",
                            "description": "Food online desc",
                        },
                    },
                    "quantity": 1,
                    }
                ],
                mode='payment',
                currency='INR',
                metadata={'food_online_order_id':order.order_number,'food_online_payment_id':payment_object.id},
                billing_address_collection='required',
                success_url=request.build_absolute_uri(reverse('payment_success')),
                cancel_url=request.build_absolute_uri(reverse('payment_cancel'))
            )
            print("checkout_session",checkout_session.id)

            payment_object.transaction_id = checkout_session.id
            payment_object.save()
            
            return redirect(checkout_session.url)
            #{'amount': 88200, 'amount_due': 88200, 'amount_paid': 0, 'attempts': 0, 'created_at': 1720291345, 'currency': 'INR', 'entity': 'order', 'id': 'order_OVRv4hdayHCXko', 'notes': [], 'offer_id': None, 'receipt': None, 'status': 'created'}
    else:
        print("**** form errors",order_form.errors())
        return HttpResponse(status=400)
    
def payment_success(request):
    return render(request,'orders/success.html')

def payment_cancel(request):
    return render(request,'orders/cancel.html')

def update_payment_status(payment_id,status):
    payment = get_object_or_404(Payment,pk=payment_id)
    payment.status = status
    payment.save()
    return payment

def update_order_status(order_id,status):
    order = get_object_or_404(Order,order_number=order_id)
    order.status = status
    order.is_ordered = True
    order.save()
    return order

def create_ordered_food(order,payment):
    user = get_object_or_404(User,pk=order.user_id)
    cart_items = Cart.objects.filter(user=user).order_by('created_at')
    for items in cart_items:
        OrderedFood.objects.create(
            user=user,
            order=order,
            payment=payment,
            fooditem = items.fooditem,
            quantity = items.quantity,
            amount = items.fooditem.price * items.quantity
        )
    Cart.clear_cart(user)
    
    print("************ order food created ********")

@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(View):
    """
    Stripe webhook view to handle checkout session completed event.
    """

    def post(self, request, format=None):
        payload = request.body
        event = None
        print("********** web hook called **********")
        
        try:
            endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
            sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
            
            print("****** inside webhook event type is ",event.type)
            
            if event.type == 'checkout.session.completed':
                order_number = event.data.object.metadata['food_online_order_id']
                payment_id = event.data.object.metadata['food_online_payment_id']
                payment = update_payment_status(payment_id,"completed")
                order = update_order_status(order_number,"completed")
                create_ordered_food(order,payment)

            if event.type == 'payment_intent.payment_failed' or event.type == 'payment_intent.canceled':
                order_number = event.data.object.metadata['food_online_order_id']
                payment_id = event.data.object.metadata['food_online_payment_id']
                update_payment_status(payment_id,"failed")
                update_order_status(order_number,"canceled")

            return HttpResponse(status=200)     
        except ValueError as e:
            # Invalid payload
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            print('Error verifying webhook signature: {}'.format(str(e)))
            return HttpResponse(status=400)


# @csrf_exempt
# def stripe_webhook(request):
#   payload = request.body
#   event = None
#   print("********** web hook called **********")

#   try:
#     endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
#     sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
#     event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
#     order_number = event.data.metadata['food_online_order_id']
#     print("inside webhook event type is ",event.type)
#     print("*** inside webhook *** order number ",order_number)
#     order = get_object_or_404(Order,order_number=order_number)
#     if event.type == 'payment_intent.succeeded':
#         order.status = "completed"   
#     if event.type == 'payment_intent.payment_failed' or event.type == 'payment_intent.canceled':
#        order.status = "cancelled"
#     order.save()
       
#   except ValueError as e:
#     # Invalid payload
#     return HttpResponse(status=400)
#   except stripe.error.SignatureVerificationError as e:
#     # Invalid signature
#     print('Error verifying webhook signature: {}'.format(str(e)))
#     return HttpResponse(status=400)
    
    


#   # Handle the event
  
     
     
    
#     # Then define and call a method to handle the successful payment intent.
#     # handle_payment_intent_succeeded(payment_intent)

  