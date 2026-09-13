from django.db import models

# Create your models here.
from django.utils import timezone

from account.models import Agent, Customer, User


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
        "shipment_module.PolList",
        on_delete=models.PROTECT,
        related_name="sea_shipments_pol",
        verbose_name="P.O.L",
        help_text="Port of Loading - بندر بارگیری",
    )
    pod = models.ForeignKey(
        "shipment_module.PodList",
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
    console = models.ForeignKey(
        "shipment_module.Console",
        on_delete=models.PROTECT,
        related_name="sea_shipments",
        verbose_name="Console",
        blank=True,
        null=True,
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
    ]
    mode = models.CharField(
        max_length=3,
        choices=SHIPMENT_MODE,
        default="fcl",
        verbose_name="Mode",
    )

    MOVEMENT_TYPE = [
        ("cy-cy", "CY / CY"),
        ("cy-cfs", "CY / CFS"),
        ("cfs-cy", "CFS / CY"),
        ("cfs-cfs", "CFS / CFS"),
        ("dr-cy", "Door / CY"),
        ("dr-dr", "Door / Door"),
    ]
    movement = models.CharField(
        max_length=10,
        choices=MOVEMENT_TYPE,
        default="cy-cy",
        verbose_name="Movement",
        help_text="نوع سرویس حمل",
    )

    place_of_receipt = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Place of Receipt",
        help_text="محل تحویل بار به کشتیرانی",
    )
    final_destination = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Final Destination",
        help_text="مقصد نهایی (مثل گمرک شهریار)",
    )

    BL_RELEASE_TYPE = [
        ("original", "Original B/L"),
        ("telex", "Telex Release / Surrendered"),
        ("waybill", "Express / Sea Waybill"),
    ]
    bl_release = models.CharField(
        max_length=10,
        choices=BL_RELEASE_TYPE,
        default="original",
        verbose_name="B/L Release",
        help_text="نوع آزادسازی بارنامه",
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

    # --- کشتی و سفر ---
    vessel_name = models.CharField(
        max_length=100,
        verbose_name="Vessel",
        help_text="نام کشتی",
    )
    voyage_no = models.CharField(
        max_length=30,
        verbose_name="Voyage No",
        help_text="شماره سفر",
    )

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

    # --- طرفین بارنامه ---
    mbl_shipper = models.TextField(
        blank=True,
        null=True,
        verbose_name="MBL Shipper",
    )
    mbl_cnee = models.TextField(
        blank=True,
        null=True,
        verbose_name="MBL Consignee",
    )
    hbl_shipper = models.TextField(
        blank=True,
        null=True,
        verbose_name="HBL Shipper",
    )
    hbl_cnee = models.TextField(
        blank=True,
        null=True,
        verbose_name="HBL Consignee",
    )
    notify_party = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notify Party",
    )
    delivery_agent = models.TextField(
        blank=True,
        null=True,
        verbose_name="Delivery Agent",
        help_text="نماینده تحویل‌دهنده بار در مقصد",
    )

    # --- کانتینر ---
    container_no = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Container No",
        help_text="شماره کانتینر (چندتایی با کاما)",
    )
    container_type = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="Container Type",
        help_text="مثل 20GP / 40HC / 40NOR",
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
    )
    marks = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Marks & Numbers",
        help_text="مثل N/M",
    )
    commodity = models.TextField(
        verbose_name="Commodity",
        help_text="شرح کالا",
    )
    hscode = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="HS Code",
    )
    gw = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        verbose_name="G.W (Kg)",
        help_text="وزن ناخالص",
    )
    vol = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        verbose_name="Volume (CBM)",
    )
    cw = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Chargeable W / R.T",
        help_text="وزن محاسباتی - Revenue Ton (برای LCL)",
    )

    # --- تاریخ ها ---
    etd = models.DateField(
        blank=True,
        null=True,
        verbose_name="ETD",
    )
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
    ata = models.DateField(
        blank=True,
        null=True,
        verbose_name="ATA",
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
        self.calculate_totals()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ref} | {self.vessel_name}/{self.voyage_no} | {self.mbl_no or self.hbl_no}"

    class Meta:
        verbose_name = "Sea Shipment"
        verbose_name_plural = "1. Sea Shipments"
        ordering = ["-created_at"]


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
