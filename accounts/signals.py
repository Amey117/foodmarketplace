from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfile,User

@receiver(post_save,sender=User)
def create_profile_receiver(sender,instance,created,**kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        print("user profile is created !")
    else:
        try:
            profile = UserProfile.objects.get(user=instance)
            profile.save()
        except:
            # if the user do not have an profile
            UserProfile.objects.create(user=instance)
            print("profile does not exist but created it now!")    
        print("user is updated !")    
