from django.conf.urls.defaults import *
from django.conf import settings

from django.contrib.auth.views import logout

from website.views import *
 
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    (r'^media_f/(.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT }),
    (r'^img_f/(.*)$', 'django.views.static.serve', { 'document_root': settings.IMAGE_ROOT }),
    (r'^css_f/(.*)$', 'django.views.static.serve', { 'document_root': settings.CSS_ROOT }),

    ('^$', home),
    ('^hello/$',hello),
    (r'^logout/$', logout),
    
    (r'^admin/', include(admin.site.urls)),
)
