from django.core.exceptions import ValidationError
import os

def validate_file_type(value):
    allowed_list = ['png','jpeg','jpg']
    if value.name.split('.')[-1].lower() not in allowed_list:
        # then the file type is invalid 
        raise ValidationError(f"File type invalid , supported for following types {allowed_list}")
    
