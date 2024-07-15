from django.urls import path
from accounts import views as AccountViews
from .views import *
urlpatterns=[
    path('',AccountViews.customer_dashboard,name="customerdashboard"),
    path('profile/',cprofile,name='cprofile')
]