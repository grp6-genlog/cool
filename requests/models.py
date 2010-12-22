from django.db import models

STATUS_CHOICES = (
    ('P', 'Pending'),
    ('C', 'Cancelled'),
)

class Request(models.Model):
    user = models.ForeignKey('profiles.UserProfile')
    departure_point_lat = models.FloatField()
    departure_point_long = models.FloatField()
    departure_range = models.FloatField()
    arrival_point_lat = models.FloatField()
    arrival_point_long = models.FloatField()
    arrival_range = models.FloatField()
    arrival_time = models.DateTimeField()
    max_delay = models.IntegerField() # in sec
    nb_requested_seats = models.IntegerField(default=1, blank=True)
    cancellation_margin = models.DateTimeField()
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P', blank=True)
    
    def __unicode__(self):
        return u'%s %s %d' % (self.user.user.first_name, self.user.user.last_name, self.id)
    
    class Meta:
        ordering = ['arrival_time']
        
