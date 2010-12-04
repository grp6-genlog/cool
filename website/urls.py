from django.conf.urls.defaults import *

from website.views import *

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    ('^$', home),
    ('^hello/$',hello),
    ('^time/$',current_datetime),
    (r'^time/plus/(\d{1,2})/$', hours_ahead),
    
    (r'^admin/', include(admin.site.urls)),
)
