from pathlib import Path
import os

SECRET_KEY = '0e68e5cf42012608bcb293a433498d30031675c83ad132f5183c7d0291320ca7'

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = True

TIME_ZONE = 'UTC'

STATICFILES_DIRS = (str(BASE_DIR.joinpath('static')),)

STATIC_URL = 'static/'
