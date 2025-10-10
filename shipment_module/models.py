from django.db import models
from django.urls import reverse

from account.models import User, Customer, Shipper, Consignee


# Create your models here.
class Shipment(models.Model):
    ref = models.CharField(max_length=255, verbose_name="Ref.No.")
    client = models.ForeignKey(
        to=Customer,
        related_name="shipment_client",
        on_delete=models.PROTECT,
        verbose_name="Client",
        blank=True,
        null=True,
    )
    sp = models.ForeignKey(
        to=User,
        related_name="shipment_sp",
        on_delete=models.PROTECT,
        verbose_name="S/P",
        blank=True,
        null=True
    )
    inq_sent = models.BooleanField(default=False, verbose_name="INQ SENT")
    inq_replied = models.BooleanField(default=False, verbose_name="INQ REPLIED")
    confirm_date = models.DateField(blank=True, null=True, verbose_name="Confirmation Date")
    via = models.CharField(max_length=255, null=True, blank=True, verbose_name="VIA")
    carrier = models.CharField(max_length=255, null=True, blank=True, verbose_name="Carrier")
    console = models.BooleanField(default=False, verbose_name="Console")
    console_no = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Console No"
    )  # TODO: auto console match
    mawb = models.CharField(max_length=255, verbose_name="MAWB", blank=True, null=True)
    hawb = models.CharField(max_length=255, verbose_name="HAWB", blank=True, null=True)
    etdw = models.DateField(blank=True, null=True, verbose_name="ETD W")
    etd = models.DateField(blank=True, null=True, verbose_name="ETD")
    eta = models.DateField(blank=True, null=True, verbose_name="ETA")
    transfer_time = models.DateField(blank=True, null=True, verbose_name="Transfer Time")
    pol = models.ForeignKey(to='PolList', on_delete=models.CASCADE, verbose_name="Pol", blank=True,
                            null=True)
    pod = models.ForeignKey(to='PodList', on_delete=models.CASCADE, verbose_name="Pod", blank=True,
                            null=True)
    term = models.ForeignKey(to='TermList', on_delete=models.CASCADE, verbose_name="Term", blank=True,
                             null=True)
    pcs = models.CharField(max_length=255, verbose_name="PCS", blank=True, null=True)
    gw = models.CharField(max_length=255, verbose_name="G.W", blank=True, null=True)
    vol = models.CharField(max_length=255, verbose_name="VOL", blank=True, null=True)
    cw = models.CharField(max_length=255, null=True, blank=True, verbose_name="C.W")
    currency = models.CharField(max_length=255, null=True, blank=True, verbose_name="Currency")
    commodity = models.CharField(max_length=255, null=True, blank=True, verbose_name="Commodity")
    hshipper = models.CharField(max_length=255, null=True, blank=True, verbose_name="HShipper")
    hcnee = models.CharField(max_length=255, null=True, blank=True, verbose_name="HCnee")
    shipper = models.ForeignKey(
        to=Shipper,
        related_name="shipment_shipper",
        on_delete=models.PROTECT,
        verbose_name="Shipper",
        blank=True,
        null=True,
    )
    cnee = models.ForeignKey(
        to=Consignee,
        related_name="shipment_cnee",
        on_delete=models.PROTECT,
        verbose_name="Cnee",
        blank=True,
        null=True,
    )
    manifest_no = models.CharField(max_length=255, null=True, blank=True, verbose_name="Manifest No")
    epl_date = models.DateField(blank=True, null=True, verbose_name="EPL Date")

    class Meta:
        verbose_name = 'Shipment'
        verbose_name_plural = '1. Shipments'

    def get_absolute_url(self):
        return reverse("shipment:invoice-detail", args=[self.pk])

    def __str__(self):
        return f"{self.ref} - {self.client}"


class PolList(models.Model):
    data = models.CharField(max_length=255, verbose_name="Pol", blank=True, null=True)

    class Meta:
        verbose_name = "Pol"
        verbose_name_plural = "2. Pols"

    def __str__(self):
        return self.data


class PodList(models.Model):
    data = models.CharField(max_length=255, verbose_name="Pod", blank=True, null=True)

    class Meta:
        verbose_name = "Pod"
        verbose_name_plural = "3. Pods"

    def __str__(self):
        return self.data


class TermList(models.Model):
    data = models.CharField(max_length=255, verbose_name="Term", blank=True, null=True)

    class Meta:
        verbose_name = "Term"
        verbose_name_plural = "4. Terms"

    def __str__(self):
        return self.data
