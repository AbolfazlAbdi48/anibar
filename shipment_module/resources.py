from import_export import fields, resources
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from django.contrib.auth import get_user_model
from account.models import User, Customer, Shipper, Consignee as Cnee, Carrier
from shipment_module.models import Shipment, PolList, PodList, TermList
from import_export.widgets import Widget
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

User = get_user_model()

class ShipmentModelResource(resources.ModelResource):
    # Explicit widgets for ForeignKey & ManyToMany relationships
    pol = fields.Field(
        column_name='pol',
        attribute='pol',
        widget=ForeignKeyWidget(PolList, 'name')
    )
    pod = fields.Field(
        column_name='pod',
        attribute='pod',
        widget=ForeignKeyWidget(PodList, 'name')
    )
    term = fields.Field(
        column_name='term',
        attribute='term',
        widget=ForeignKeyWidget(TermList, 'name')
    )
    shipper = fields.Field(
        column_name='mawb_shipper',
        attribute='shipper',
        widget=ForeignKeyWidget(Shipper, 'name')
    )
    cnee = fields.Field(
        column_name='mawb_cnee',
        attribute='cnee',
        widget=ForeignKeyWidget(Cnee, 'name')
    )
    hawb_shipper = fields.Field(
        column_name='hawb_shipper',
        attribute='hawb_shipper',
        widget=ForeignKeyWidget(Shipper, 'name')
    )
    hawb_cnee = fields.Field(
        column_name='hawb_cnee',
        attribute='hawb_cnee',
        widget=ForeignKeyWidget(Cnee, 'name')
    )
    carrier = fields.Field(
        column_name='carrier',
        attribute='carrier',
        widget=ForeignKeyWidget(Carrier, 'name')
    )
    operators = fields.Field(
        column_name='operators',
        attribute='operators',
        widget=ManyToManyWidget(User, separator=',', field='username')
    )

    class Meta:
        model = Shipment
        # List all model fields you want imported/exported
        # You can exclude the auto/computed ones
        exclude = (
            'id',
            'sp',  # set automatically from logged-in user
            'transit_time',  # computed
            'confirm_date',  # auto when confirmation checked
        )
        import_id_fields = ('ref',)
        skip_unchanged = True
        report_skipped = True