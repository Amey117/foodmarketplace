from django.urls import path,include
from . import views
urlpatterns=[
    path('place_order',views.place_order,name="place_order"),
    path('payment',views.payment_form,name="payment_form"),
    path('intent/create',views.create_intent,name="create_intent"),
    path('payment/success/<str:order_number>',views.payment_success,name="payment_success"),
    path('payment/cancel',views.payment_cancel,name="payment_cancel"),
    path('stripe/webhook/',views.StripeWebhookView.as_view(),name="stripe_webhook")
]