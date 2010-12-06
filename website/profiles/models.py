from django.db import models

from django.contrib.auth.models import User #as OfficialUser
from django.db.models.signals import post_save


GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female'),
)

"""
class User(models.Model):
    
    login = models.CharField(max_length=70, primary_key=True)
    password = models.CharField(max_length=50)
    number_of_seats = models.IntegerField()
    date_of_birth = models.DateField(blank=True)
    smoker = models.BooleanField(default=False, blank=True)
    communities = models.CharField(max_length=100, blank=True)
    money_per_km = models.FloatField()
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    bank_account_number = models.CharField(max_length=30)
    car_id = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20)
    car_description = models.TextField(max_length=500)
    smartphone_id = models.CharField(max_length=100)
    mail = models.EmailField()

    def __unicode__(self):
        return u'%s' % (self.name)
"""
class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    
    number_of_seats = models.IntegerField()
    date_of_birth = models.DateField(blank=True)
    smoker = models.BooleanField(default=False, blank=True)
    communities = models.CharField(max_length=100, blank=True)
    money_per_km = models.FloatField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    bank_account_number = models.CharField(max_length=30)
    account_balance = models.FloatField(default=0.0, blank=True)
    car_id = models.CharField(max_length=50, blank=True)
    phone_number = models.CharField(max_length=20)
    car_description = models.TextField(max_length=500, blank=True)
    smartphone_id = models.CharField(max_length=100, blank=True)
    
    def __str__(self):  
          return "%s's profile" % self.user  

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])
          
"""          
def create_user_profile(sender, instance, created, **kwargs):  
    if created:  
       profile, created = UserProfile.objects.get_or_create(user=instance)  

post_save.connect(create_user_profile, sender=User)
"""
