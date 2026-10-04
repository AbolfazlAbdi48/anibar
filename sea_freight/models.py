from django.db import models, transaction

# Create your models here.
from django.utils import timezone

from account.models import Agent, Customer, User, Shipper, Consignee


class SeaShipment(models.Model):
    """
    مدل اصلی پرونده حمل و نقل دریایی (Sea Freight)
    ساختار مشابه AirShipment با دسته‌بندی: Basic / Cargo & Vessel / Invoices
    """

    # ============================================================
    #  ۱) BASIC DETAILS
    # ============================================================

    ref = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Ref",
        help_text="شماره رفرانس داخلی پرونده",
    )

    # --- مدل های مشترک ---
    client = models.ForeignKey(
        to=Customer,
        on_delete=models.PROTECT,
        related_name="sea_shipments",
        verbose_name="Client",
    )
    sp = models.ForeignKey(
        to=User,
        on_delete=models.PROTECT,
        related_name="sea_shipments",
        verbose_name="S/P",
    )
    pol = models.ForeignKey(
        "sea_freight.SeaPolList",
        on_delete=models.PROTECT,
        related_name="sea_shipments_pol",
        verbose_name="P.O.L",
        help_text="Port of Loading - بندر بارگیری",
    )
    pod = models.ForeignKey(
        "sea_freight.SeaPodList",
        on_delete=models.PROTECT,
        related_name="sea_shipments_pod",
        verbose_name="P.O.D",
        help_text="Port of Discharge - بندر تخلیه",
    )
    term = models.ForeignKey(
        "shipment_module.TermList",
        on_delete=models.PROTECT,
        related_name="sea_shipments",
        verbose_name="Term",
        help_text="Incoterms",
    )
    agent = models.ForeignKey(
        to=Agent,
        on_delete=models.PROTECT,
        related_name="sea_shipments",
        verbose_name="Agent",
        blank=True,
        null=True,
    )

    # --- فیلدهای اختصاصی دریایی ---
    SHIPMENT_MODE = [
        ("fcl", "FCL"),
        ("lcl", "LCL"),
        ("bb", "Break Bulk"),
        ("b", "Bulk"),
    ]
    mode = models.CharField(
        max_length=3,
        choices=SHIPMENT_MODE,
        default="fcl",
        verbose_name="Mode",
    )

    priority = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="Priority",
    )

    inq_replied = models.BooleanField(
        default=False,
        verbose_name="Inquiry Replied (RPL)",
    )
    confirmed = models.BooleanField(
        default=False,
        verbose_name="CFM (Confirmed)",
    )
    cfm_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="CFM Date",
    )

    # ============================================================
    #  ۲) CARGO & VESSEL DETAILS
    # ============================================================
    # --- بارنامه ها ---
    mbl_no = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="MBL No",
        help_text="Master Bill of Lading",
    )
    hbl_no = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="HBL No",
        help_text="House Bill of Lading",
    )
    booking_no = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Booking No",
        help_text="شماره بوکینگ / S/O",
    )
    manifest_no = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Manifest No",
    )
    hbl_shipper = models.ForeignKey(
        to=Shipper,
        related_name="sea_freight_hbl_shipper",
        on_delete=models.PROTECT,
        verbose_name="HBL Shipper",
        blank=True,
        null=True,
    )
    hbl_cnee = models.ForeignKey(
        to=Consignee,
        related_name="sea_freight_hbl_cnee",
        on_delete=models.PROTECT,
        verbose_name="HBL Cnee",
        blank=True,
        null=True,
    )
    notify_party = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notify Party",
    )

    # --- کانتینر ---
    container_no = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Container No",
        help_text="شماره کانتینر (چندتایی با کاما)",
    )
    seal_no = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Seal No",
    )

    # --- مشخصات بار ---
    pcs = models.CharField(
        max_length=50,
        verbose_name="Packages",
        help_text="تعداد و نوع بسته بندی مثل: 2 WOODEN CASES",
        null=True,
        blank=True
    )
    gw = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        verbose_name="G.W (Kg)",
        help_text="وزن ناخالص",
        null=True,
        blank=True
    )
    vol = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        verbose_name="Volume (CBM)",
        null=True,
        blank=True
    )

    # --- تاریخ ها ---
    atd = models.DateField(
        blank=True,
        null=True,
        verbose_name="ATD",
        help_text="تاریخ واقعی حرکت (Shipped on Board)",
    )
    eta = models.DateField(
        blank=True,
        null=True,
        verbose_name="ETA",
    )

    # ============================================================
    #  ۳) INVOICES & CHARGES
    # ============================================================

    FREIGHT_TERM = [
        ("prepaid", "Prepaid"),
        ("collect", "Collect"),
    ]
    freight_term = models.CharField(
        max_length=10,
        choices=FREIGHT_TERM,
        default="prepaid",
        verbose_name="Freight",
    )

    currency = models.CharField(
        max_length=3,
        default="USD",
        verbose_name="Currency",
    )

    ocean_freight = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Ocean Freight",
    )
    thc_pol = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="THC (POL)",
    )
    thc_pod = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="THC (POD)",
    )
    pickup_inland = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Pickup / Inland",
    )
    customs_clearance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Customs Clearance",
    )
    do_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="D/O Fee",
    )
    transit_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Transit Fee",
    )
    other_charges = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Other Charges",
    )
    extra_charges = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Extra Charges",
    )

    total_usd = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        editable=False,
        verbose_name="Total (USD)",
    )
    carrier = models.ForeignKey(
        "sea_freight.SeaCarrier",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Carrier"
    )
    grand_total_usd = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        editable=False,
        verbose_name="Grand Total (USD)",
    )

    # --- وضعیت فactoring ---
    invoice_deadline = models.DateField(
        blank=True,
        null=True,
        verbose_name="Invoice Deadline",
    )
    invoice_issued = models.BooleanField(
        default=False,
        verbose_name="Invoice Issued",
    )
    payment_done = models.BooleanField(
        default=False,
        verbose_name="Payment Done",
    )

    operators = models.ManyToManyField(
        to=User,
        blank=True,
        related_name="operators",
        verbose_name="Operators",
    )

    # ============================================================
    #  Timestamps
    # ============================================================
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At",
    )

    # ============================================================
    #  Methods
    # ============================================================
    def calculate_totals(self):
        """محاسبه مجموع هزینه ها"""
        charges = [
            self.ocean_freight, self.thc_pol, self.thc_pod,
            self.pickup_inland, self.customs_clearance,
            self.do_fee, self.transit_fee, self.other_charges,
        ]
        self.total_usd = sum(charges)
        self.grand_total_usd = self.total_usd + (self.extra_charges or 0)

    def save(self, *args, **kwargs):
        if not self.ref:
            today = timezone.now().date()
            date_prefix = today.strftime("%y%m%d")  # e.g., "251129" (6 digits)

            with transaction.atomic():
                last = SeaShipment.objects.filter(ref__startswith=date_prefix) \
                    .select_for_update() \
                    .order_by('-ref') \
                    .first()
                if last:
                    # Extract counter from last ref (everything after the 6-digit date prefix)
                    counter_str = last.ref[6:]  # Get everything after "YYMMDD"
                    try:
                        last_counter = int(counter_str)
                    except ValueError:
                        last_counter = 0
                    counter = last_counter + 1
                else:
                    counter = 1

                # Format counter as 2 digits (00-99), then 3 digits (100+)
                if counter <= 99:
                    counter_formatted = f"{counter:02d}"  # "00", "01", ..., "99"
                else:
                    counter_formatted = f"{counter:03d}"  # "100", "101", etc.

                self.ref = f"{date_prefix}{counter_formatted}"

        self.calculate_totals()

        if self.confirmed and not self.cfm_date:
            self.cfm_date = timezone.localtime(timezone.now())

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ref} | {self.vessel_name}/{self.voyage_no} | {self.mbl_no or self.hbl_no}"

    class Meta:
        verbose_name = "Sea Shipment"
        verbose_name_plural = "1. Sea Shipments"
        ordering = ["-created_at"]


class SeaPolList(models.Model):
    data = models.CharField(max_length=255, verbose_name="Sea Pol", blank=True, null=True)
    country_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Country Name")
    country_abbr = models.CharField(max_length=5, blank=True, null=True, verbose_name="Country Abbr")
    airport_abbr = models.CharField(max_length=5, blank=True, null=True, verbose_name="Airport Abbr")

    class Meta:
        verbose_name = "Pol"
        verbose_name_plural = "7. Sea Pols"

    def __str__(self):
        return str(self.data or "")


class SeaPodList(models.Model):
    data = models.CharField(max_length=255, verbose_name="Sea Pod", blank=True, null=True)
    country_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Country Name")
    country_abbr = models.CharField(max_length=5, blank=True, null=True, verbose_name="Country Abbr")
    airport_abbr = models.CharField(max_length=5, blank=True, null=True, verbose_name="Airport Abbr")

    class Meta:
        verbose_name = "Pod"
        verbose_name_plural = "8. Sea Pods"

    def __str__(self):
        return str(self.data or "")


class SeaCarrier(models.Model):
    name = models.CharField(max_length=255, verbose_name="Sea Carrier Name")
    national_id = models.CharField(max_length=20, blank=True, null=True, verbose_name="Iran Office Address")
    abbreviation = models.CharField(max_length=10, blank=True, null=True, verbose_name="Iran Office Tel")
    description = models.TextField(blank=True, null=True, verbose_name="Description")

    class Meta:
        verbose_name = "Carrier"
        verbose_name_plural = "5. Carriers"

    def __str__(self):
        return self.name


class Container(models.Model):
    CONTAINER_TYPES = [
        ("20GP", "20' General Purpose"),
        ("40GP", "40' General Purpose"),
        ("40HQ", "40' High Cube"),
        ("20RF", "20' Reefer"),
        ("40RF", "40' Reefer"),
        ("20OT", "20' Open Top"),
        ("40OT", "40' Open Top"),
        ("40FR", "40' Flat Rack"),
    ]

    shipment = models.ForeignKey(
        SeaShipment,
        on_delete=models.CASCADE,
        related_name="containers",
        verbose_name="Sea Shipment"
    )
    container_no = models.CharField(max_length=20, verbose_name="Container No")
    seal_no = models.CharField(max_length=30, blank=True, verbose_name="Seal No")
    container_type = models.CharField(max_length=10, choices=CONTAINER_TYPES, default="40HQ", verbose_name="Type")
    gw = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Gross Weight (KG)")
    vol = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Volume (CBM)")

    class Meta:
        verbose_name = "Container"
        verbose_name_plural = "2. Containers"

    def __str__(self):
        return f"{self.container_no} ({self.container_type})"
