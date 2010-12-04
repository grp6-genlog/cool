from django.db import models

class Proposal(models.Model):
    user = models.ForeignKey('profiles.UserProfile')
    car_id = models.CharField(max_length=50)
    car_description = models.TextField(max_length=500)
    number_of_seats = models.IntegerField()
    money_per_km = models.FloatField()
    departure_time = models.DateTimeField()
    
    def __unicode__(self):
        return u'%s %d' % (self.user.name, self.id)
    
    class Meta:
        ordering = ['user']
        
class RoutePoints(models.Model):
    proposal = models.ForeignKey('Proposal')
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __unicode__(self):
        return u'%s %s' % (self.Latitude, self.Longitude) # %s ???
