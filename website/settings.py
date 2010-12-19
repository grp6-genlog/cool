# Django settings for website project.
import os, sys
"""
print "__name__ =", __name__
print "__file__ =", __file__
print "os.getpid() =", os.getpid()
print "os.getcwd() =", os.getcwd()
print "os.curdir =", os.curdir
print "sys.path =", repr(sys.path)
print "sys.modules.keys() =", repr(sys.modules.keys())
print "sys.modules.has_key('website') =", sys.modules.has_key('website')
if sys.modules.has_key('website'):
  print "sys.modules['website'].__name__ =", sys.modules['website'].__name__
  print "sys.modules['website'].__file__ =", sys.modules['website'].__file__
  print "os.environ['DJANGO_SETTINGS_MODULE'] =", os.environ.get('DJANGO_SETTINGS_MODULE', None)
"""
PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__)))

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'mysql',            # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'carpool',              # Or path to database file if using sqlite3.
        'USER': 'root',                     # Not used with sqlite3.
        'PASSWORD': 'martin',                 # Not used with sqlite3.
        'HOST': '',                     # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                     # Set to empty string for default. Not used with sqlite3.
    }
}

AUTH_PROFILE_MODULE = 'profiles.User'

EMAIL_USE_TLS = True
EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = "carpooling.cool@gmail.com"
EMAIL_HOST_PASSWORD = "genlogiscool"
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = "carpooling.cool@gmail.com"


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Brussels'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-GB'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_PATH,'media/')
IMAGE_ROOT = os.path.join(MEDIA_ROOT,'img/')
CSS_ROOT = os.path.join(MEDIA_ROOT,'css/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '5dlvqc@7&+f7&_#g19r@1t08r!@c(ahqhrt3tz25w$w5d)-%uj'

# List of callables that know how to import templates from various sources.


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.csrf.CsrfResponseMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'website.urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    #'django.contrib.sites',
    #'django.contrib.messages',
    'django.contrib.admin',
    #'django.contrib.admindocs',
    
    'website.profiles',
    'website.proposals',
    'website.requests',
    'website.offers',
    'website.rides',
    'website.evaluations',
        
    'django_extensions',
)

#global_ports = utils_port.PortObjects()
