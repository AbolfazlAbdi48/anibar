from django.db import models
from django.urls import reverse
from account.models import User, Customer, Shipper, Consignee, Carrier
from django.utils import timezone


# Create your models here.
class Shipment(models.Model):
    # 1. Basic Details
    ref = models.CharField(max_length=255, verbose_name="Ref.No.", blank=True, null=True)

    client = models.ForeignKey(
        to=Customer,
        related_name="shipment_client",
        on_delete=models.PROTECT,
        verbose_name="Client",
        blank=False,
        null=False,
    )
    sp = models.ForeignKey(
        to=User,
        related_name="shipment_sp",
        on_delete=models.PROTECT,
        verbose_name="S/P",
        blank=False,
        null=False
    )
    pol = models.ForeignKey(
        to='PolList',
        on_delete=models.CASCADE,
        verbose_name="Pol",
        blank=False,
        null=False
    )
    pod = models.ForeignKey(
        to='PodList',
        on_delete=models.CASCADE,
        verbose_name="Pod",
        blank=False,
        null=False
    )
    marketing_channel = models.CharField(
        max_length=100,
        blank=False,
        null=False,
        verbose_name="Marketing Channel"
    )

    # 2. Other Details (remain optional)
    inq_sent = models.BooleanField(default=False, verbose_name="INQ SENT")
    inq_replied = models.BooleanField(default=False, verbose_name="INQ REPLIED")

    confirmation = models.BooleanField(default=False, verbose_name="Confirmed")
    confirm_date = models.DateTimeField(blank=True, null=True, verbose_name="Confirmation Date")

    via = models.CharField(max_length=255, null=True, blank=True, verbose_name="VIA")

    carrier = models.ForeignKey(
        to=Carrier,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Carrier"
    )

    console = models.BooleanField(default=False, verbose_name="Console")
    console_no = models.CharField(max_length=255, null=True, blank=True, verbose_name="Console No")

    mawb = models.CharField(max_length=255, verbose_name="MAWB", blank=True, null=True)
    hawb = models.CharField(max_length=255, verbose_name="HAWB", blank=True, null=True)

    etdw = models.DateField(blank=True, null=True, verbose_name="ETD W")
    etd = models.DateField(blank=True, null=True, verbose_name="ETD")
    eta = models.DateField(blank=True, null=True, verbose_name="ETA")

    term = models.ForeignKey(to='TermList', on_delete=models.CASCADE, verbose_name="Term", blank=True, null=True)

    pcs = models.CharField(max_length=255, verbose_name="PCS", blank=True, null=True)
    gw = models.CharField(max_length=255, verbose_name="G.W", blank=True, null=True)
    vol = models.CharField(max_length=255, verbose_name="VOL", blank=True, null=True)
    cw = models.CharField(max_length=255, null=True, blank=True, verbose_name="C.W")
    currency = models.CharField(max_length=255, null=True, blank=True, verbose_name="Currency")
    commodity = models.CharField(max_length=255, null=True, blank=True, verbose_name="Commodity")

    shipper = models.ForeignKey(
        to=Shipper,
        related_name="shipment_shipper",
        on_delete=models.PROTECT,
        verbose_name="MAWB Shipper",
        blank=True,
        null=True,
    )
    cnee = models.ForeignKey(
        to=Consignee,
        related_name="shipment_cnee",
        on_delete=models.PROTECT,
        verbose_name="MAWB Cnee",
        blank=True,
        null=True,
    )

    hawb_shipper = models.ForeignKey(
        to=Shipper,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="hawb_shipments",
        verbose_name="HAWB Shipper"
    )
    hawb_cnee = models.ForeignKey(
        to=Consignee,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="hawb_cnee_shipments",
        verbose_name="HAWB Cnee"
    )

    manifest_no = models.CharField(max_length=255, null=True, blank=True, verbose_name="Manifest No")

    hscode = models.CharField(max_length=50, blank=True, null=True, verbose_name="HS Code")
    extra_charges = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Extra Charges")

    operators = models.ManyToManyField(User, blank=True, related_name="operator_shipments", verbose_name="Operators")

    transit_time = models.IntegerField(blank=True, null=True, verbose_name="Transit Time (days)")

    airfreight = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    pickup = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    custom_clearance = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    do_clearance_ika = models.DecimalField(
        "D/O + Clearance IKA (IRR)", max_digits=15, decimal_places=0, null=True, blank=True
    )
    transfer_fee = models.DecimalField(
        "Transfer Fee (2%)", max_digits=12, decimal_places=2, null=True, blank=True
    )
    other_charges = models.DecimalField(
        "Other Charges (S/AWB, AAI, AMS, AWB/PCA)", max_digits=12, decimal_places=2, null=True, blank=True
    )
    total_usd = models.DecimalField("Total (USD)", max_digits=12, decimal_places=2, null=True, blank=True)
    grand_total_usd = models.DecimalField("Grand Total (USD)", max_digits=12, decimal_places=2, null=True, blank=True)


    class Meta:
        verbose_name = 'Shipment'
        verbose_name_plural = '1. Shipments'

    def __str__(self):
        return f"{self.ref or 'NoRef'} - {self.client or 'NoClient'}"

    def get_absolute_url(self):
        return reverse("shipment:invoice-detail", args=[self.pk])

    def save(self, *args, **kwargs):
        if not self.ref:
            today = timezone.now().date()
            date_prefix = today.strftime("%y%m%d")

            # Count how many shipments with same prefix exist
            today_shipments = Shipment.objects.filter(ref__startswith=date_prefix).count()
            counter = today_shipments + 1

            if counter <= 99:
                suffix = f"{counter:02d}"  # two digits up to 99
            else:
                suffix = f"{counter:03d}"  # three digits after 99

            self.ref = f"{date_prefix}{suffix}"

        if not self.sp_id and hasattr(self, "_current_user"):
            self.sp = self._current_user

        if self.confirmation and not self.confirm_date:
            self.confirm_date = timezone.localtime(timezone.now())

        if self.eta and self.etd:
            self.transit_time = (self.etdw - self.eta).days
        else:
            self.transit_time = None

        super().save(*args, **kwargs)



class PolList(models.Model):
    data = models.CharField(max_length=255, verbose_name="Pol", blank=True, null=True)
    country_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Country Name")
    country_abbr = models.CharField(max_length=5, blank=True, null=True, verbose_name="Country Abbr")
    airport_abbr = models.CharField(max_length=5, blank=True, null=True, verbose_name="Airport Abbr")

    class Meta:
        verbose_name = "Pol"
        verbose_name_plural = "2. Pols"

    def __str__(self):
        return self.data


class PodList(models.Model):
    data = models.CharField(max_length=255, verbose_name="Pod", blank=True, null=True)
    country_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Country Name")
    country_abbr = models.CharField(max_length=5, blank=True, null=True, verbose_name="Country Abbr")
    airport_abbr = models.CharField(max_length=5, blank=True, null=True, verbose_name="Airport Abbr")

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
