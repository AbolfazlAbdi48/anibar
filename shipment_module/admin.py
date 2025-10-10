from import_export.admin import ImportExportModelAdmin
from django.contrib import admin
from .models import Shipment, PolList, PodList, TermList
from .resources import ShipmentModelResource


@admin.register(Shipment)
class ShipmentAdmin(ImportExportModelAdmin):
    resource_class = ShipmentModelResource
    list_display = (
        'ref', 'client__name', 'confirm_date', 'inq_sent', 'inq_replied', 'via', 'carrier', 'console', 'console_no',
        'mawb', 'hawb', 'etdw', 'etd', 'eta', 'pol', 'pod', 'term', 'pcs', 'gw', 'vol', 'cw',
        'currency', 'commodity', 'hshipper', 'hcnee', 'shipper', 'cnee', 'manifest_no', 'epl_date'
    )
    list_filter = ('eta', 'console_no', "inq_sent")
    search_fields = ('client__name', 'sp__username', "mawb", "hawb")
    # fieldsets = (
    #     ('1. Basic Details', {"fields": ('ref', 'client', 'commodity', 'pcs', 'gw', 'vol', 'cw')}),
    #     ('2. Transport & Routing Information', {
    #         "fields": ('via', 'carrier', 'pol', 'pod', 'term', 'eta', 'etd', 'etdw')
    #     }),
    #     ('3. Documentation & Consolidation', {"fields": ('console', 'console_no', 'mawb', 'hawb', 'manifest_no')}),
    #     ('4. Shipper & Consignee Details', {"fields": ('shipper', 'Cnee', 'hshipper', 'hcnee')}),
    #     ('5. Status & Inquiry Tracking', {"fields": ('inq_sent', 'inq_replied', 'confirm_date', 'epl_date')}),
    #     ('6. Financial & Currency Info', {"fields": ('currency',)}),
    # )


@admin.register(PolList)
class PolListAdmin(admin.ModelAdmin):
    pass


@admin.register(PodList)
class PodListAdmin(admin.ModelAdmin):
    pass


@admin.register(TermList)
class TermListAdmin(admin.ModelAdmin):
    pass
