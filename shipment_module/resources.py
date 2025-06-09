from import_export import fields, resources
from import_export.widgets import ForeignKeyWidget

from account.models import User
from shipment_module.models import Shipment

from import_export.widgets import DateWidget, Widget
from datetime import datetime


# Register your models here.

class MultiFormatDateWidget(Widget):
    def __init__(self, formats=None):
        self.formats = formats or ['%Y-%m-%d', '%Y.%m.%d', '%Y/%m/%d', '%d/%m/%Y']

    def clean(self, value, row=None, *args, **kwargs):
        if not value:
            return None
        value = str(value).strip()
        for fmt in self.formats:
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue
        raise ValueError(f"فرمت تاریخ '{value}' با هیچ‌یک از فرمت‌های تعریف‌شده مطابقت ندارد: {self.formats}")

    def render(self, value, **kwargs):
        if not value:
            return ""
        return value.strftime(self.formats[0])


class GetOrCreateUserWidget(ForeignKeyWidget):
    def clean(self, value, row=None, *args, **kwargs):
        if not value:
            return None
        user, created = User.objects.get_or_create(username=value)
        return user


class ShipmentModelResource(resources.ModelResource):
    client = fields.Field(
        column_name='client',
        attribute='client',
        widget=GetOrCreateUserWidget(User, 'username')
    )

    sp = fields.Field(
        column_name='sp',
        attribute='sp',
        widget=ForeignKeyWidget(User, 'username')
    )

    confirm_date = fields.Field(
        column_name='confirm_date',
        attribute='confirm_date',
        widget=DateWidget(format='%Y.%m.%d')
    )

    etdw = fields.Field(
        column_name='etdw',
        attribute='etdw',
        widget=MultiFormatDateWidget()
    )

    etd = fields.Field(
        column_name='etd',
        attribute='etd',
        widget=MultiFormatDateWidget()
    )

    eta = fields.Field(
        column_name='eta',
        attribute='eta',
        widget=MultiFormatDateWidget()
    )

    transfer_time = fields.Field(
        column_name='transfer_time',
        attribute='transfer_time',
        widget=MultiFormatDateWidget()
    )

    class Meta:
        model = Shipment
        fields = (
            'id', 'ref', 'client', 'sp', 'inq_sent', 'inq_replied', 'confirm_date', 'via', 'carrier', 'console',
            'console_no',
            'mawb', 'hawb', 'etdw', 'etd', 'eta', 'transfer_time', 'pol', 'pod', 'term', 'pcs', 'gw', 'vol', 'cw',
            'currency', 'commodity', 'hshipper', 'hcnee', 'shipper', 'Cnee', 'manifest_no', 'epl_date'
        )
