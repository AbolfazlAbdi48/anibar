from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.
class User(AbstractUser):
    is_agent = models.BooleanField(default=False, verbose_name=_('Agent'))
