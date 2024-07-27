from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage,EmailMultiAlternatives
from django.core.exceptions import PermissionDenied
from django.conf import settings


def detech_user(user):
    if user.is_anonymous:
        redirect_url = '/'
    elif user.role == 1 :
        # user is vendor trying to login

        redirect_url = 'vendor_dashboard'
    elif user.role == 2:
        redirect_url = 'customer_dashboard'
    elif user.role == None and user.is_superadmin:
        redirect_url = '/admin'
    
    return redirect_url

def send_verification_email(request,user):
    """
    this function with create the email verification data inc encoded user id
    """
    current_site =  get_current_site(request)
    mail_subject = "Please activate your account"
    message = render_to_string('accounts/email/acc_verification.html',{
        'user':user,
        'domain':current_site,
        'uid':urlsafe_base64_encode(force_bytes(user.pk)),
        'token':default_token_generator.make_token(user)
    })
    to_email = user.email
    mail = EmailMultiAlternatives(mail_subject,from_email=settings.DEFAULT_FROM_EMAIL,to=[to_email])
    mail.attach_alternative(message, "text/html")
    mail.send()

def send_password_reset_link(request,user):
    """
    this function will send the password verification link to the user
    """
    current_site =  get_current_site(request)
    mail_subject = "Forgot Password"
    message = render_to_string('accounts/email/reset_password.html',{
        'user':user,
        'domain':current_site,
        'uid':urlsafe_base64_encode(force_bytes(user.pk)),
        'token':default_token_generator.make_token(user)
    })
    to_email = user.email
    mail = EmailMultiAlternatives(mail_subject,from_email=settings.DEFAULT_FROM_EMAIL,to=[to_email])
    mail.attach_alternative(message, "text/html")
    mail.send()

def send_vendor_onboard_notification(subject,comment,vendor):
    mail_subject = subject
    message = render_to_string('accounts/email/vendor_onboard.html',{
        'vendor':vendor,
        "comment":comment
    })
    to_email = vendor.user.email
    mail = EmailMultiAlternatives(mail_subject,from_email=settings.DEFAULT_FROM_EMAIL,to=[to_email])
    mail.attach_alternative(message, "text/html")
    mail.send()


def send_notification(email,subject,context,template):
    mail_subject = subject
    message = render_to_string(template,context)
    to_email = email
    mail = EmailMultiAlternatives(mail_subject,from_email=settings.DEFAULT_FROM_EMAIL,to=to_email)
    mail.attach_alternative(message, "text/html")
    mail.send()


# this is a custom decorater to restrict the vendor from accessing customer page and vice versa

def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied


def check_role_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied