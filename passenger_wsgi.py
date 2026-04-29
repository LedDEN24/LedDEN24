# -*- coding: utf-8 -*-
"""
REG.RU shared hosting WSGI entrypoint.

Before enabling this file, replace the two placeholder paths below:
1) PROJECT_ROOT  -> absolute path to the folder where manage.py lives
2) VENV_SITE_PACKAGES -> absolute path to your virtualenv site-packages

Example paths on REG.RU usually look like:
    /var/www/LOGIN/data/www/your-domain.ru
    /var/www/LOGIN/data/djangoenv/lib/python3.10/site-packages
"""
import os
import sys

PROJECT_ROOT = '/var/www/LOGIN/data/www/your-domain.ru'
VENV_SITE_PACKAGES = '/var/www/LOGIN/data/djangoenv/lib/python3.10/site-packages'

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if VENV_SITE_PACKAGES not in sys.path:
    sys.path.insert(1, VENV_SITE_PACKAGES)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
