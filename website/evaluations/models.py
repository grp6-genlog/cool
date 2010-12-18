from django.db import models

class Evaluation(models.Model):
    ride = models.ForeignKey('rides.Ride', null=True)
    user_from = models.ForeignKey('profiles.UserProfile', related_name='user_from')
    user_to = models.ForeignKey('profiles.UserProfile', related_name='user_to')
    rating = models.IntegerField(null=True)
    content = models.TextField(max_length=500, null=True, blank=True)
    ride_time = models.DateTimeField(null=True)
    locked = models.BooleanField(default=True)

    
    def __unicode__(self):
        return u'%s -> %s' % (self.user_from.user.username, self.user_to.user.username)
    
