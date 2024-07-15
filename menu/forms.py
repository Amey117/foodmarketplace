from typing import Any
from django import forms
from .models import Category,FoodItem

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name',"description"]

class FoodForm(forms.ModelForm):

    def __init__(self,*args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = None
        if self.instance and self.instance.pk:
            # form is opned in edit mode so we knew which vendor it belongs so we would fetch all its category
            print(" **** food form is opned in edit mode")
            self.fields['category'].queryset = Category.objects.filter(vendor=self.instance.vendor)
        else:
            print("new form opned")
        
        


    class Meta:
        model=FoodItem
        fields = ['food_title','category','description','price','food_image','is_available']