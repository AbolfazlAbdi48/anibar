from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from account.models import User, Customer, Consignee, Shipper, Carrier, Agent
from shipment_module.models import Shipment


class ShipmentInline(admin.TabularInline):
    model = Shipment
    fk_name = "client"
    extra = 0
    can_delete = False
    show_change_link = True

    fields = (
        "ref",
        "confirmed",
        "confirm_date",
        "pol",
        "pod",
        "etd",
        "eta",
        "mode",
        "priority",
    )

    readonly_fields = fields


# -------------------------
# User Admin
# -------------------------
class UserModelAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_agent",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = ("username", "email", "first_name", "last_name", "is_staff", "is_agent")
    list_filter = ("is_staff", "is_agent", "is_active", "groups")
    search_fields = ("username", "email", "first_name", "last_name")
    list_editable = ("is_agent",)


# -------------------------
# Customer Admin
# -------------------------
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "address", "marketing_channel")
    search_fields = ("name", "email", "phone")
    ordering = ("name",)

    inlines = [ShipmentInline]


# -------------------------
# Consignee Admin
# -------------------------
class ConsigneeAdmin(admin.ModelAdmin):
    list_display = ("name", "national_id", "email", "phone")
    search_fields = ("name", "national_id", "email", "phone")
    ordering = ("name",)
    fieldsets = (
        (None, {"fields": ("name", "national_id", "email", "postal_code", "phone", "address")}),
    )


# -------------------------
# Shipper Admin
# -------------------------
class ShipperAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "address")
    search_fields = ("name", "email", "phone")
    ordering = ("name",)


# -------------------------
# Carrier Admin
# -------------------------
class CarrierAdmin(admin.ModelAdmin):
    list_display = ("name", "abbreviation", "national_id")
    search_fields = ("name", "abbreviation", "national_id")
    ordering = ("name",)


class AgentAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "code", "email", "phone")
    search_fields = ("name", "code")


admin.site.register(User, UserModelAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Consignee, ConsigneeAdmin)
admin.site.register(Shipper, ShipperAdmin)
admin.site.register(Carrier, CarrierAdmin)
admin.site.register(Agent, AgentAdmin)
