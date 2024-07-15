from datetime import date,datetime
from typing import Iterable
from django.db import models
from django.db.models import F
from accounts.models import User,UserProfile
from accounts.utils import send_vendor_onboard_notification
# Create your models here.


class Vendor(models.Model):
    user = models.OneToOneField(User,related_name='user',on_delete=models.CASCADE)
    user_profile = models.OneToOneField(UserProfile,related_name='user_profile',on_delete=models.CASCADE)
    vendor_name = models.CharField(max_length=100)
    vendor_slug = models.SlugField(max_length=100,blank=True)
    vendor_license = models.ImageField(upload_to="vendor/license")
    is_approved = models.BooleanField(null=True)
    comment = models.CharField(max_length=200,default="",null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateField(auto_now_add=True)


    def __str__(self) -> str:
        return self.vendor_name
    
    def is_open(self):
        today = date.today()
        weekday_number = today.weekday() + 1 # it gives 0 for monday
        current_day_opening_hrs = OpeningHour.objects.filter(vendor=self,day=weekday_number)
        current_date = datetime.now()
        is_open_now = False
        for hrs in current_day_opening_hrs:
            if not hrs.is_closed and datetime.strptime(hrs.from_hour,'%I:%M %p').time() <= current_date.time() <= datetime.strptime(hrs.to_hour,'%I:%M %p').time():
                is_open_now=True
                break
            else:
                is_open_now=False
        return is_open_now
    
    def save(self,*args,**kwargs):
        if self.pk is not None:
            #update
            #current status is already saved in db
            #self is an state that is not stored yet in db
            subject = "Vendor Registration Request"
            current_status = Vendor.objects.get(pk=self.pk)            
            if self.is_approved is not None and current_status.is_approved != self.is_approved:
                if self.is_approved == True and self.user.is_active:
                    print("Approved!")
                    send_vendor_onboard_notification(subject,self.comment,self)
                else:
                    print("Rejected!")
                    self.comment += "You have not yet Activated your user account."
                    send_vendor_onboard_notification(subject,self.comment,self)
        return super(Vendor,self).save(*args,**kwargs)

DAYS = [
    (1,"Monday"),
    (2,"Tuesday"),
    (3,"Wednesday"),
    (4,"Thrusday"),
    (5,"Friday"),
    (6,"Saturday"),
    (7,"Sunday")
]

# class DynamicTimeManager(models.Manager):
#     def get_queryset(self):
#         # Helper function to convert time strings to datetime.time objects
#         def convert_time(time_str):
#             breakpoint()
#             return datetime.strptime(time_str, "%I:%M %p").time()
    

#         # Annotate each record with a sortable time value
#         queryset = super().get_queryset()
#         return queryset.annotate(
#             sortable_time=convert_time(F("from_hour") )
#         ).order_by('sortable_time')

# value,label
HOUR_OF_DAY_24 = [('12:00 AM', '12:00 AM'), ('12:30 AM', '12:30 AM'), ('01:00 AM', '01:00 AM'), ('01:30 AM', '01:30 AM'), ('02:00 AM', '02:00 AM'), ('02:30 AM', '02:30 AM'), ('03:00 AM', '03:00 AM'), ('03:30 AM', '03:30 AM'), ('04:00 AM', '04:00 AM'), ('04:30 AM', '04:30 AM'), ('05:00 AM', '05:00 AM'), ('05:30 AM', '05:30 AM'), ('06:00 AM', '06:00 AM'), ('06:30 AM', '06:30 AM'), ('07:00 AM', '07:00 AM'), ('07:30 AM', '07:30 AM'), ('08:00 AM', '08:00 AM'), ('08:30 AM', '08:30 AM'), ('09:00 AM', '09:00 AM'), ('09:30 AM', '09:30 AM'), ('10:00 AM', '10:00 AM'), ('10:30 AM', '10:30 AM'), ('11:00 AM', '11:00 AM'), ('11:30 AM', '11:30 AM'), ('12:00 PM', '12:00 PM'), ('12:30 PM', '12:30 PM'), ('01:00 PM', '01:00 PM'), ('01:30 PM', '01:30 PM'), ('02:00 PM', '02:00 PM'), ('02:30 PM', '02:30 PM'), ('03:00 PM', '03:00 PM'), ('03:30 PM', '03:30 PM'), ('04:00 PM', '04:00 PM'), ('04:30 PM', '04:30 PM'), ('05:00 PM', '05:00 PM'), ('05:30 PM', '05:30 PM'), ('06:00 PM', '06:00 PM'), ('06:30 PM', '06:30 PM'), ('07:00 PM', '07:00 PM'), ('07:30 PM', '07:30 PM'), ('08:00 PM', '08:00 PM'), ('08:30 PM', '08:30 PM'), ('09:00 PM', '09:00 PM'), ('09:30 PM', '09:30 PM'), ('10:00 PM', '10:00 PM'), ('10:30 PM', '10:30 PM'), ('11:00 PM', '11:00 PM'), ('11:30 PM', '11:30 PM')]
class OpeningHour(models.Model):
    vendor = models.ForeignKey(Vendor,on_delete=models.CASCADE)
    day = models.IntegerField(choices=DAYS)
    from_hour = models.CharField(choices=HOUR_OF_DAY_24,max_length=100,blank=True)
    to_hour = models.CharField(choices=HOUR_OF_DAY_24,max_length=100,blank=True)
    is_closed = models.BooleanField(default=False)

    # objects = DynamicTimeManager()

    def __str__(self) -> str:
        return self.get_day_display() # it gives label of the choice fields
    

    class Meta:
        ordering = ('day','from_hour')
        unique_together = ('day','from_hour','to_hour','vendor')