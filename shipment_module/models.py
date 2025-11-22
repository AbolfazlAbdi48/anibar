from django.db import models, transaction
from django.urls import reverse
from account.models import User, Customer, Shipper, Consignee, Carrier, Agent
from django.utils import timezone
from django.utils.html import format_html


# Create your models here.
class Shipment(models.Model):
    # 1. Basic Details
    ref = models.CharField(max_length=255, verbose_name="Ref.No.", blank=True, null=True, unique=True)

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

    # 2. Inquiry / Confirmation fields (we drop inq_sent and standardize naming)
    # If you still need inq_sent, keep it before running migrations.
    # inq_sent = models.BooleanField(default=False, verbose_name="INQ SENT")  # removed per your request

    inq_replied = models.BooleanField(default=False, verbose_name="INQ REPLIED")

    # Use 'confirmed' as the boolean (was named 'confirmation' previously)
    confirmed = models.BooleanField(default=False, verbose_name="Confirmed")
    confirm_date = models.DateTimeField(blank=True, null=True, verbose_name="Confirmation Date")

    via = models.CharField(max_length=255, null=True, blank=True, verbose_name="VIA")

    carrier = models.ForeignKey(
        to=Carrier,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Carrier"
    )

    # 3. Console & Agent
    # Replaced console boolean+console_no with a FK to Console model (Console table)
    console = models.ForeignKey(
        to="Console",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Console"
    )

    # Agent relation
    agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Agent")

    # 4. Master / House (keep field names to avoid destructive rename; verbose names adjusted)
    mawb = models.CharField(max_length=255, verbose_name="Master", blank=True, null=True)  # was MAWB
    hawb = models.CharField(max_length=255, verbose_name="House", blank=True, null=True)   # was HAWB

    # new first master/house fields (appear under VIA)
    first_master = models.CharField(max_length=255, verbose_name="First Master", blank=True, null=True)
    first_house = models.CharField(max_length=255, verbose_name="First House", blank=True, null=True)

    # 5. Dates
    etdw = models.DateField(blank=True, null=True, verbose_name="ETD W")
    etd = models.DateField(blank=True, null=True, verbose_name="ETD")
    eta = models.DateField(blank=True, null=True, verbose_name="ETA")

    # 6. Term and mode
    term = models.ForeignKey(to='TermList', on_delete=models.CASCADE, verbose_name="Term", blank=True, null=True)
    MODE_CHOICES = [
        ("air_single", "Air - Single"),
        ("air_console", "Air - Console"),
        ("sea_fcl", "Sea - FCL"),
        ("sea_lcl", "Sea - LCL"),
        ("sea_bb", "Sea - BB"),
        ("sea_bulk", "Sea - Bulk"),
        ("land_ltl", "Land - LTL"),
        ("land_ftl", "Land - FTL"),
        ("land_rail", "Land - Rail"),
    ]

    mode = models.CharField(
        max_length=20,
        choices=MODE_CHOICES,
        blank=True,
        null=True,
        verbose_name="Mode",
    )

    # 7. Cargo & weights (kept as strings to avoid type-change migrations)
    pcs = models.CharField(max_length=255, verbose_name="PCS", blank=True, null=True)
    gw = models.CharField(max_length=255, verbose_name="G.W", blank=True, null=True)
    first_gw = models.CharField(max_length=255, verbose_name="First G.W", blank=True, null=True)
    vol = models.CharField(max_length=255, verbose_name="VOL", blank=True, null=True)
    cw = models.CharField(max_length=255, null=True, blank=True, verbose_name="C.W")
    first_cw = models.CharField(max_length=255, null=True, blank=True, verbose_name="First C.W")
    currency = models.CharField(max_length=255, null=True, blank=True, verbose_name="Currency")
    commodity = models.CharField(max_length=255, null=True, blank=True, verbose_name="Commodity")

    # 8. Parties
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

    # 9. Charges & totals (financials)
    airfreight = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    pickup = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    custom_clearance = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    do_clearance_ika = models.DecimalField("D/O + Clearance IKA (IRR)", max_digits=15, decimal_places=0, null=True, blank=True)
    transfer_fee = models.DecimalField("Transfer Fee (2%)", max_digits=12, decimal_places=2, null=True, blank=True)
    other_charges = models.DecimalField("Other Charges (S/AWB, AAI, AMS, AWB/PCA)", max_digits=12, decimal_places=2, null=True, blank=True)
    total_usd = models.DecimalField("Total (USD)", max_digits=12, decimal_places=2, null=True, blank=True)
    grand_total_usd = models.DecimalField("Grand Total (USD)", max_digits=12, decimal_places=2, null=True, blank=True)

    # 10. Added priority field (visual)
    PRIORITY_CHOICES = [
        ("green", "Green"),
        ("yellow", "Yellow"),
        ("red", "Red"),
    ]
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="green", verbose_name="Priority")

    # Meta
    class Meta:
        verbose_name = 'Shipment'
        verbose_name_plural = '1. Shipments'
        ordering = ["-created_at"]

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.ref or 'NoRef'} - {self.client or 'NoClient'}"

    def get_absolute_url(self):
        return reverse("shipment:invoice-detail", args=[self.pk])

    # models.py (Shipment)
    def get_manifest_url(self):
        return reverse("shipment:manifest-detail", args=[self.pk])

    def colored_priority_badge(self):
        colors = {"green": "#6cc24a", "yellow": "#ffd43b", "red": "#ff4d4f"}
        color = colors.get(self.priority, "#ddd")
        return format_html('<span style="padding:3px 8px;border-radius:6px;background:{};">{}</span>', color, self.get_priority_display())
    colored_priority_badge.short_description = "Priority"

    def save(self, *args, **kwargs):
        if not self.ref:
            today = timezone.now().date()
            date_prefix = today.strftime("%y%m%d")

            with transaction.atomic():
                last = Shipment.objects.filter(ref__startswith=date_prefix) \
                                    .select_for_update() \
                                    .order_by('-ref') \
                                    .first()
                if last:
                    # get last 3 digits; works with existing data  (002, 015, 123)
                    try:
                        last_counter = int(last.ref[-3:])
                    except ValueError:
                        last_counter = 0
                    counter = last_counter + 1
                else:
                    counter = 1

                self.ref = f"{date_prefix}{counter:03d}"

        if not getattr(self, "sp_id", None) and hasattr(self, "_current_user"):
            self.sp = self._current_user

        # auto-set confirm_date when confirmed
        if self.confirmed and not self.confirm_date:
            self.confirm_date = timezone.localtime(timezone.now())

        # auto calc transit time (etdw - eta)
        if self.etdw and self.eta:
            try:
                self.transit_time = (self.etdw - self.eta).days
            except Exception:
                self.transit_time = None
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
        return str(self.data or "")


class PodList(models.Model):
    data = models.CharField(max_length=255, verbose_name="Pod", blank=True, null=True)
    country_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Country Name")
    country_abbr = models.CharField(max_length=5, blank=True, null=True, verbose_name="Country Abbr")
    airport_abbr = models.CharField(max_length=5, blank=True, null=True, verbose_name="Airport Abbr")

    class Meta:
        verbose_name = "Pod"
        verbose_name_plural = "3. Pods"

    def __str__(self):
        return str(self.data or "")


class TermList(models.Model):
    data = models.CharField(max_length=255, verbose_name="Term", blank=True, null=True)

    class Meta:
        verbose_name = "Term"
        verbose_name_plural = "4. Terms"

    def __str__(self):
        return str(self.data or "")




class Console(models.Model):
    code = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Console"
        verbose_name_plural = "5. Consoles"
        ordering = ("-created_at",)

    def __str__(self):
        return str(self.data or "")


class Charge(models.Model):
    shipment = models.ForeignKey("Shipment", related_name="charges", on_delete=models.CASCADE)
    description = models.CharField(max_length=250)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default="USD")
    payer = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Charge"
        verbose_name_plural = "6. Charges"

    def __str__(self):
        ref = getattr(self.shipment, "ref", None) or "NoRef"
        desc = self.description or ""
        amount = self.amount or ""
        currency = self.currency or ""
        return f"{ref} • {desc} {amount} {currency}"



class ShipmentComment(models.Model):
    shipment = models.ForeignKey(
        "Shipment",
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Shipment"
    )
    author_name = models.CharField(
        max_length=100,
        verbose_name="Author",
        editable=False
    )
    text = models.TextField(verbose_name="Comment")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Auto-fill author_name if we have the current user attached from admin
        if not self.author_name and hasattr(self, "_current_user"):
            self.author_name = (
                self._current_user.get_full_name()
                or self._current_user.username
            )
        super().save(*args, **kwargs)

    def __str__(self):
        author = self.author_name or "Unknown"
        ref = getattr(self.shipment, "ref", None) or "NoRef"
        return f"{author} → {ref}"