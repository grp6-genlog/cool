from django.db import models

class Evaluation(models.Model):
    ride = models.ForeignKey('rides.Ride')
    user_from = models.ForeignKey('profiles.UserProfile', related_name='user_from')
    user_to = models.ForeignKey('profiles.UserProfile', related_name='user_to')
    rating = models.IntegerField()
    content = models.TextField(max_length=500)
    time = models.DateTimeField()
    locked = models.BooleanField(default=True)

    
    def __unicode__(self):
        return u'%s -> %s' % (self.user_from.name, self.user_to.name)
    
