from django.db import models

class Request(models.Model):
    user = models.ForeignKey('profiles.UserProfile')
    departure_point_lat = models.FloatField()
    departure_point_long = models.FloatField()
    departure_range = models.FloatField()
    arrival_point_lat = models.FloatField()
    arrival_point_long = models.FloatField()
    arrival_range = models.FloatField()
    departure_time = models.DateTimeField()
    max_delay = models.IntegerField()
    nb_requested_seats = models.IntegerField(default=1, blank=True)
    cancellation_margin = models.DateTimeField()
    
    def __unicode__(self):
        return u'%s %d' % (self.user.name, self.id)
    
    class Meta:
        ordering = ['user']
        
