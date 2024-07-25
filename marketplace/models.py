from django.db import models
from accounts.models import User
from menu.models import FoodItem
# Create your models here.

class Cart(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    fooditem = models.ForeignKey(FoodItem,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateField(auto_now_add=True)

    @classmethod
    def clear_cart(cls,user):
        # this functions delete cart elements
        cart_items = Cart.objects.filter(user=user)
        cart_items.delete()
        

    def __str__(self) -> str:
        return self.user.first_name
    
class Tax(models.Model):
    tax_type = models.CharField(max_length=20,unique=True)
    tax_percentage = models.DecimalField(decimal_places=2,max_digits=4,verbose_name='Tax Percentage (%)')
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.tax_type