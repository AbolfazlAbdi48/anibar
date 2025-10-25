from urllib import request
from import_export.admin import ImportExportModelAdmin
from django.contrib import admin
from .models import Shipment, PolList, PodList, TermList
from .resources import ShipmentModelResource


@admin.register(Shipment)
class ShipmentAdmin(ImportExportModelAdmin):
    resource_class = ShipmentModelResource
    filter_horizontal = ('operators',)

    # -------------------------------
    # Display configuration
    # -------------------------------
    list_display = (
        'ref', 'client', 'sp', 'confirmation', 'confirm_date',
        'inq_sent', 'inq_replied', 'carrier', 'console', 'console_no',
        'mawb', 'hawb', 'etdw', 'etd', 'eta', 'pol', 'pod', 'term',
        'pcs', 'gw', 'vol', 'cw', 'currency', 'commodity',
        'shipper', 'cnee', 'hawb_shipper', 'hawb_cnee',
        'extra_charges', 'transit_time', 'marketing_channel',
    )

    list_filter = (
        'confirmation', 'inq_sent', 'inq_replied', 'carrier',
        'console', 'pol', 'pod', 'term', 'eta', 'sp'
    )

    search_fields = (
        'ref', 'client__name', 'sp__username',
        'mawb', 'hawb',
        'shipper__name', 'cnee__name',
        'hawb_shipper__name', 'hawb_cnee__name',
        'carrier__name'
    )

    search_help_text = "Search by Ref, Client, S/P, MAWB, HAWB, Shipper, Consignee, or Carrier"
    list_per_page = 50

    # -------------------------------
    # Field organization
    # -------------------------------
    fieldsets = (
    # 1. Basic Details
    ('1. Basic Details', {
        "fields": (
            'ref', 'client', 'sp', 'pol', 'pod', 'marketing_channel'
        )
    }),

    # 2. Cargo Details (merged with all others)
    ('2. Cargo Details', {
        "fields": (
            # Old Cargo Details
            'commodity', 'pcs', 'gw', 'vol', 'cw', 'currency', 'hscode',

            # Transport & Routing
            'via', 'carrier', 'term', 'etdw', 'etd', 'eta', 'transit_time',

            # Operators & Marketing
            'operators',

            # Documentation & Consolidation
            'console', 'console_no', 'mawb', 'hawb', 'manifest_no',

            # Parties Involved
            'shipper', 'cnee', 'hawb_shipper', 'hawb_cnee',

            # Financial & Status
            'extra_charges', 'inq_sent', 'inq_replied', 'confirmation', 'confirm_date',
        )
    }),

    # 8. Charges (USD)
    ('8. Charges (USD)', {
        "fields": (
            'airfreight', 'pickup', 'custom_clearance',
            'transfer_fee', 'other_charges', 'total_usd', 'grand_total_usd'
        )
    }),

    # 9. D/O & Clearance (IRR)
    ('9. D/O & Clearance (IRR)', {
        "fields": ('do_clearance_ika',)
    }),
)
    # -------------------------------

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        if not request.user.is_anonymous:
            initial['sp'] = request.user.pk
        return initial


# -------------------------------
# Supporting models
# -------------------------------
@admin.register(PolList)
class PolListAdmin(admin.ModelAdmin):
    list_display = ("data", "country_name", "country_abbr", "airport_abbr")
    search_fields = ("data", "country_name", "airport_abbr")
    ordering = ("data",)


@admin.register(PodList)
class PodListAdmin(admin.ModelAdmin):
    list_display = ("data", "country_name", "country_abbr", "airport_abbr")
    search_fields = ("data", "country_name", "airport_abbr")
    ordering = ("data",)


@admin.register(TermList)
class TermListAdmin(admin.ModelAdmin):
    list_display = ("data",)
    search_fields = ("data",)
    ordering = ("data",)