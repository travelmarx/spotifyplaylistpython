import os

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '0e68e5cf42012608bcb293a433498d30031675c83ad132f5183c7d0291320ca7'

DEBUG = False
ALLOWED_HOSTS = [os.environ['WEBSITE_HOSTNAME']] if 'WEBSITE_HOSTNAME' in os.environ else []
CSRF_TRUSTED_ORIGINS = ['https://'+ os.environ['WEBSITE_HOSTNAME']] if 'WEBSITE_HOSTNAME' in os.environ else []