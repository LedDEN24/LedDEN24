from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    phone = models.CharField("Телефон", max_length=32, blank=True)
    inn = models.CharField("ИНН", max_length=12, blank=True, db_index=True)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
