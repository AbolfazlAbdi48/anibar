from import_export.admin import ImportExportModelAdmin
from django.contrib import admin
from .models import Shipment
from .resources import ShipmentModelResource


@admin.register(Shipment)
class ShipmentAdmin(ImportExportModelAdmin):
    resource_class = ShipmentModelResource
    list_display = (
        'ref', 'client__username', 'confirm_date', 'inq_sent', 'inq_replied', 'via', 'carrier', 'console', 'console_no',
        'mawb', 'hawb', 'etdw', 'etd', 'eta', 'pol', 'pod', 'term', 'pcs', 'gw', 'vol', 'cw',
        'currency', 'commodity', 'hshipper', 'hcnee', 'shipper', 'Cnee', 'manifest_no', 'epl_date'
    )
    list_filter = ('eta', 'console_no')
    search_fields = ('client__username', 'sp__username')
