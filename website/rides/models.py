from django.db import models

class Ride(models.Model):
    offer = models.ForeignKey('offers.Offer')
    manuel_mode = models.BooleanField(default=False)
    ride_started = models.BooleanField(default=False)
    
    def __unicode__(self):
        return u'%s %s' % (self.offer.request.user.name, self.offer.proposal.user.name)
    
