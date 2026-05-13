from __future__ import annotations

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "real_estate_check.settings")

app = Celery("real_estate_check")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
