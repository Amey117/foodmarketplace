from typing import Any, Mapping
from django import forms
from django.core.exceptions import ValidationError
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList
from .models import User, UserProfile
from .validators import validate_file_type


class userRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        c_password = cleaned_data.get("confirm_password")
        if password != c_password:
            raise ValidationError("Password does not match")

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "username", "password"]


class vendorRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        c_password = cleaned_data.get("confirm_password")
        if password != c_password:
            raise ValidationError("Password does not match")

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "username", "password"]


class UserProfileForm(forms.ModelForm):
    profile_picture = forms.FileField(validators=[validate_file_type],required=False)
    cover_photo = forms.FileField(validators=[validate_file_type],required=False)
    latitude = forms.CharField(widget=forms.TextInput(attrs={"readonly": "readonly"}),required=False)
    longitude = forms.CharField(widget=forms.TextInput(attrs={"readonly": "readonly"}),required=False)
    address = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Start typing','required':'required'}))
    class Meta:
        model = UserProfile
        exclude = ["user", "created_at", "updated_at"]

class UserInfoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [ 'first_name','last_name','phone_number']