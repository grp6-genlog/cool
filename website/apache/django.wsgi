import os
import sys

sys.path.insert(0, '/home/mart/cool/website')
sys.path.insert(0, '/home/mart/cool')

os.environ['DJANGO_SETTINGS_MODULE'] = 'website.settings'


import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

