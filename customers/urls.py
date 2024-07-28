from django.urls import path
from accounts import views as AccountViews
from .views import *
urlpatterns=[
    path('',AccountViews.customer_dashboard,name="customerdashboard"),
    path('profile/',cprofile,name='cprofile'),
    path('my-orders/',my_orders,name="my_orders"),
    path('order-details/<int:order_number>',order_details,name="order_details")
]