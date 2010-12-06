from django.db import models

STATUS_CHOICES = (
    ('P', 'Pending'),
    ('C', 'Canceled'),
    ('A', 'agreedByBoth'),
    ('D', 'discarded'),
)

class Offer(models.Model):
    request = models.ForeignKey('requests.Request')
    proposal = models.ForeignKey('proposals.Proposal')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    driver_ok = models.BooleanField(default=False)
    non_driver_ok = models.BooleanField(default=False)
    
    def __unicode__(self):
        return u'%s %s' % (self.request.user.name, self.proposal.user.name)
    
    class Meta:
        ordering = ['request']
        