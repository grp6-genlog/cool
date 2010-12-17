from django.db import models


STATUS_CHOICES = (
    ('P', 'Pending'),
    ('C', 'Cancelled'),
)


class Proposal(models.Model):
    user = models.ForeignKey('profiles.UserProfile')
    car_id = models.CharField(max_length=50)
    car_description = models.TextField(max_length=500)
    number_of_seats = models.IntegerField()
    money_per_km = models.FloatField()
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P', blank=True)
    
    def __unicode__(self):
        return u'%s %s %d' % (self.user.user.first_name, self.user.user.last_name, self.id)
    
    class Meta:
        ordering = ['user']
        
        
class RoutePoints(models.Model):
    proposal = models.ForeignKey('Proposal')
    latitude = models.FloatField()
    longitude = models.FloatField()
    order = models.IntegerField()

    def __unicode__(self):
        return u'%s %s %s' % (self.latitude, self.longitude, self.order) # %s ???
        
    class Meta:
        ordering = ['order']
        
