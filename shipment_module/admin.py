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
        ('1. Basic Details', {
            "fields": (
                'ref', 'client', 'sp', 'commodity', 'pcs', 'gw', 'vol', 'cw', 'currency', 'hscode'
            )
        }),
        ('2. Transport & Routing', {
            "fields": (
                'via', 'carrier', 'pol', 'pod', 'term', 'etdw', 'etd', 'eta', 'transit_time'
            )
        }),
        ('3. Operators & Marketing', {
            "fields": (
                'operators', 'marketing_channel'
            )
        }),
        ('4. Documentation & Consolidation', {
            "fields": (
                'console', 'console_no', 'mawb', 'hawb', 'manifest_no'
            )
        }),
        ('5. Parties Involved', {
            "fields": (
                'shipper', 'cnee', 'hawb_shipper', 'hawb_cnee'
            )
        }),
        ('6. Financial & Status', {
            "fields": (
                'extra_charges', 'inq_sent', 'inq_replied', 'confirmation', 'confirm_date'
            )
        }),
    )

    # -------------------------------
    # Auto-assign logged-in user to S/P
    # -------------------------------
    def save_model(self, request, obj, form, change):
        if not obj.sp_id:
            obj._current_user = request.user
        super().save_model(request, obj, form, change)


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