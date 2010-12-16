from django.db import models

STATUS_CHOICES = (
    ('P', 'Pending'),
    ('C', 'Cancelled'),
    ('A', 'agreedByBoth'),
    ('D', 'Discarded'),
    ('F', 'Finished'),
)

class Offer(models.Model):
    request = models.ForeignKey('requests.Request')
    proposal = models.ForeignKey('proposals.Proposal')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    driver_ok = models.BooleanField(default=False)
    non_driver_ok = models.BooleanField(default=False)
    pickup_point_lat = models.FloatField()
    pickup_point_long = models.FloatField()
    pickup_time = models.DateTimeField()
    drop_point_lat = models.FloatField()
    drop_point_long = models.FloatField()
    drop_time = models.DateTimeField()
    total_fee = models.FloatField()
    
    def __unicode__(self):
        return u'%s %s' % (self.request.user.user.first_name, self.proposal.user.user.last_name)
    
    class Meta:
        ordering = ['request']
        
