from django.conf.urls.defaults import *
from django.conf import settings

from website.views import *

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    (r'^media_f/(.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT }),
    (r'^img_f/(.*)$', 'django.views.static.serve', { 'document_root': settings.IMAGE_ROOT }),
    (r'^css_f/(.*)$', 'django.views.static.serve', { 'document_root': settings.CSS_ROOT }),

    ('^$', home),
    ('^hello/$',hello),
    ('^time/$',current_datetime),
    (r'^time/plus/(\d{1,2})/$', hours_ahead),
    
    (r'^admin/', include(admin.site.urls)),
)
