import os
import sys

PROJECT_PATH = os.path.dirname(os.path.abspath(os.path.join(os.path.dirname(__file__))))

sys.path.insert(0, PROJECT_PATH)
sys.path.insert(0, os.path.dirname(PROJECT_PATH))

os.environ['DJANGO_SETTINGS_MODULE'] = 'website.settings'


import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

