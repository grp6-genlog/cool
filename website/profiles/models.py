from django.db import models

from django.contrib.auth.models import User
from django.db.models.signals import post_save


GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female'),
)


class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    
    number_of_seats = models.IntegerField()
    date_of_birth = models.DateField(blank=True, null=True)
    smoker = models.BooleanField(default=False, blank=True)
    communities = models.CharField(max_length=100, blank=True, null=True)
    money_per_km = models.FloatField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    bank_account_number = models.CharField(max_length=30)
    account_balance = models.FloatField(default=0.0)
    car_id = models.CharField(max_length=50, blank=True, null=True)
    phone_number = models.CharField(max_length=20)
    car_description = models.TextField(max_length=500, blank=True, null=True)
    smartphone_id = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):  
          return "%s's profile" % self.user

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])
          
          
"""          
def create_user_profile(sender, instance, created, **kwargs):  
    if created:  
       profile, created = UserProfile.objects.get_or_create(user=instance)  

post_save.connect(create_user_profile, sender=User)
"""
