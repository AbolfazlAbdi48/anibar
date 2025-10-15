from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from account.models import User, Customer, Consignee, Shipper, Carrier


# -------------------------
# User Admin
# -------------------------
@admin.register(User)
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
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "address")
    search_fields = ("name", "email", "phone")
    ordering = ("name",)


# -------------------------
# Consignee Admin
# -------------------------
@admin.register(Consignee)
class ConsigneeAdmin(admin.ModelAdmin):
    list_display = ("name", "national_id", "email", "phone")
    search_fields = ("name", "national_id", "email", "phone")
    ordering = ("name",)
    fieldsets = (
        (None, {"fields": ("name", "national_id", "email", "phone", "address")}),
    )


# -------------------------
# Shipper Admin
# -------------------------
@admin.register(Shipper)
class ShipperAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "address")
    search_fields = ("name", "email", "phone")
    ordering = ("name",)


# -------------------------
# Carrier Admin
# -------------------------
@admin.register(Carrier)
class CarrierAdmin(admin.ModelAdmin):
    list_display = ("name", "abbreviation", "national_id")
    search_fields = ("name", "abbreviation", "national_id")
    ordering = ("name",)
