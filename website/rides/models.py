from django.db import models

""" Structure of the sql table for the rides """
class Ride(models.Model):
    offer = models.ForeignKey('offers.Offer')
    manuel_mode = models.BooleanField(default=False)
    ride_started = models.BooleanField(default=False)
    
    def __unicode__(self):
        return u'%s %s' % (self.offer.request.user.user.username, self.offer.proposal.user.user.username)
    
