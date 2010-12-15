from django.db import models

class Request(models.Model):
    user = models.ForeignKey('profiles.UserProfile')
    departure_point_lat = models.FloatField()
    departure_point_long = models.FloatField()
    departure_range = models.FloatField()
    arrival_point_lat = models.FloatField()
    arrival_point_long = models.FloatField()
    arrival_range = models.FloatField()
    arrival_time = models.DateTimeField()
    max_delay = models.DateTimeField()
    nb_requested_seats = models.IntegerField(default=1, blank=True)
    cancellation_margin = models.DateTimeField()
    
    def __unicode__(self):
        return u'%s %s %d' % (self.user.user.first_name, self.user.user.last_name, self.id)
    
    class Meta:
        ordering = ['user']
        
