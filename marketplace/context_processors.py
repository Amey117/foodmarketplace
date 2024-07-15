from menu.models import FoodItem
from .models import Cart,Tax


def cart_counter(request):
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart_items = Cart.objects.filter(user=request.user)
            if cart_items:
                for cart_item in cart_items:
                    cart_count+=cart_item.quantity
            else:
                cart_count=0
        except:
            cart_count=0
    return {"cart_count":cart_count}

def get_cart_amount(request):
    sub_total=0
    grand_total=0
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            sub_total = sub_total + (item.fooditem.price * item.quantity)
        get_tax = Tax.objects.filter(is_active=True)
        taxes_list = []
        grand_total = sub_total
        for tax in get_tax:
            taxes = dict()
            tax_type = tax.tax_type
            tax_per = tax.tax_percentage
            tax_amount = round((tax_per*sub_total)/100,2)
            taxes['type'] = tax_type
            taxes['per'] = float(tax_per.to_eng_string())
            taxes ['tax_amount'] = float(tax_amount.to_eng_string())
            taxes_list.append(taxes)
            grand_total+=tax_amount
        print("taxes_list *****     ====>",taxes_list)
    else:
        taxes_list=[]
        grand_total = 0
    return {"sub_total":sub_total,"grand_total":grand_total,"taxes_list":taxes_list}
