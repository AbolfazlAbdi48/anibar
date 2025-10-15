from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.
class User(AbstractUser):
    is_agent = models.BooleanField(default=False, verbose_name=_('Agent'))

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "1. Users"


class Customer(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    about = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('About'))
    address = models.TextField(blank=True, null=True, verbose_name=_('Address'))
    country = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Country'))
    phone = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('Phone Number'))
    email = models.EmailField(max_length=100, blank=True, null=True, verbose_name=_('Email'))

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "2. Customers"

    def __str__(self):
        return self.name


class Shipper(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    address = models.TextField(blank=True, null=True, verbose_name=_('Address'))
    country = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Country'))
    phone = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('Phone Number'))
    email = models.EmailField(max_length=100, blank=True, null=True, verbose_name=_('Email'))

    class Meta:
        verbose_name = "Shipper"
        verbose_name_plural = "2. Shippers"

    def __str__(self):
        return self.name


class Consignee(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    company = models.CharField(max_length=255, verbose_name=_('Company'))
    address = models.TextField(blank=True, null=True, verbose_name=_('Address'))
    country = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Country'))
    phone = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('Phone Number'))
    email = models.EmailField(max_length=100, blank=True, null=True, verbose_name=_('Email'))
    national_id = models.CharField(max_length=20, blank=True, null=True, verbose_name="National ID")

    class Meta:
        verbose_name = "Consignee"
        verbose_name_plural = "3. Consignees"

    def __str__(self):
        return self.name


class Carrier(models.Model):
    name = models.CharField(max_length=255, verbose_name="Carrier Name")
    national_id = models.CharField(max_length=20, blank=True, null=True, verbose_name="National ID")
    abbreviation = models.CharField(max_length=10, blank=True, null=True, verbose_name="Abbreviation")

    class Meta:
        verbose_name = "Carrier"
        verbose_name_plural = "4. Carriers"

    def __str__(self):
        return self.name