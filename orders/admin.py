from django.contrib import admin
from .models import Payment,Order,OrderedFood


class OrderedFoodAdmin(admin.TabularInline):
    model = OrderedFood
    readonly_fields = ['fooditem','quantity','amount']
    extra = 0
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number','first_name','last_name','total','status','is_ordered']
    inlines = [OrderedFoodAdmin]

admin.site.register(Payment)
admin.site.register(Order,OrderAdmin)
admin.site.register(OrderedFood)

