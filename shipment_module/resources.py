from import_export import fields, resources
from import_export.widgets import ForeignKeyWidget

from account.models import User, Customer, Shipper, Consignee
from shipment_module.models import Shipment, PolList, PodList, TermList

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
        user, created = User.objects.get_or_create(username=value.lower(), is_agent=True)
        return user


class GetOrCreateCustomerWidget(ForeignKeyWidget):
    def clean(self, value, row=None, *args, **kwargs):
        if not value:
            return None
        customer, created = Customer.objects.get_or_create(name=value.strip())
        return customer


class GetOrCreatePartyWidget(ForeignKeyWidget):
    """
    ویجت برای مدل های Shipper, Consignee و Customer.
    مقدار خالی را به None تبدیل می کند و بر اساس فیلد 'name' نمونه را پیدا/ایجاد می کند.
    """

    def clean(self, value, row=None, *args, **kwargs):
        if not value or str(value).strip() == '':
            return None

        model = self.model
        cleaned_value = str(value).strip()
        instance, created = model.objects.get_or_create(**{'name': cleaned_value})

        return instance


class GetOrCreateListWidget(ForeignKeyWidget):
    def clean(self, value, row=None, *args, **kwargs):
        if not value:
            return None

        model = self.model

        cleaned_value = str(value).strip()

        instance, created = model.objects.get_or_create(**{'data': cleaned_value})

        return instance


class ShipmentModelResource(resources.ModelResource):
    client = fields.Field(
        column_name='client',
        attribute='client',
        widget=GetOrCreateCustomerWidget(Customer, 'name')
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

    pol = fields.Field(
        column_name='pol',
        attribute='pol',
        widget=GetOrCreateListWidget(PolList, 'data')
    )

    pod = fields.Field(
        column_name='pod',
        attribute='pod',
        widget=GetOrCreateListWidget(PodList, 'data')
    )

    term = fields.Field(
        column_name='term',
        attribute='term',
        widget=GetOrCreateListWidget(TermList, 'data')
    )

    shipper = fields.Field(
        column_name='shipper',
        attribute='shipper',
        widget=GetOrCreatePartyWidget(Shipper, 'name')
    )

    cnee = fields.Field(
        column_name='Cnee',
        attribute='cnee',
        widget=GetOrCreatePartyWidget(Consignee, 'name')
    )

    class Meta:
        model = Shipment
        fields = (
            'id', 'ref', 'client', 'sp', 'inq_sent', 'inq_replied', 'confirm_date', 'via', 'carrier', 'console',
            'console_no',
            'mawb', 'hawb', 'etdw', 'etd', 'eta', 'transfer_time', 'pol', 'pod', 'term', 'pcs', 'gw', 'vol', 'cw',
            'currency', 'commodity', 'hshipper', 'hcnee', 'shipper', 'cnee', 'manifest_no', 'epl_date'
        )
