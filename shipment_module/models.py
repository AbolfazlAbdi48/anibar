from django.db import models

from account.models import User


# Create your models here.
class Shipment(models.Model):
    ref = models.CharField(max_length=255, verbose_name="Ref.No.")
    client = models.ForeignKey(
        to=User,
        related_name="shipment_client",
        on_delete=models.PROTECT,
        verbose_name="Client"
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
    mawb = models.CharField(max_length=255, verbose_name="MAWB")
    hawb = models.CharField(max_length=255, verbose_name="HAWB")
    etdw = models.DateField(blank=True, null=True, verbose_name="ETD W")
    etd = models.DateField(blank=True, null=True, verbose_name="ETD")
    eta = models.DateField(blank=True, null=True, verbose_name="ETA")
    transfer_time = models.DateField(blank=True, null=True, verbose_name="Transfer Time")
    pol = models.CharField(max_length=255, verbose_name="Pol")
    pod = models.CharField(max_length=255, verbose_name="Pod")
    term = models.CharField(max_length=255, verbose_name="Term")
    pcs = models.CharField(max_length=255, verbose_name="PCS")
    gw = models.CharField(max_length=255, verbose_name="G.W")
    vol = models.CharField(max_length=255, verbose_name="VOL")
    cw = models.CharField(max_length=255, null=True, blank=True, verbose_name="C.W")
    currency = models.CharField(max_length=255, null=True, blank=True, verbose_name="Currency")
    commodity = models.CharField(max_length=255, null=True, blank=True, verbose_name="Currency")
    hshipper = models.CharField(max_length=255, null=True, blank=True, verbose_name="HShipper")
    hcnee = models.CharField(max_length=255, null=True, blank=True, verbose_name="HCnee")
    shipper = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Shipper"
    )  # TODO: foreign key to User model
    Cnee = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Cnee"
    )  # TODO: foreign key to User model
    manifest_no = models.CharField(max_length=255, null=True, blank=True, verbose_name="Manifest No")
    epl_date = models.DateField(blank=True, null=True, verbose_name="ETD")

    class Meta:
        verbose_name = 'Shipment'
        verbose_name_plural = 'Shipments'

    def __str__(self):
        return f"{self.ref} - {self.client.username}"
