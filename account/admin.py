from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from account.models import User, Customer, Consignee, Shipper


# Register your models here.
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
    list_editable = ("is_agent",)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    pass


@admin.register(Consignee)
class ConsigneeAdmin(admin.ModelAdmin):
    pass


@admin.register(Shipper)
class ShipperAdmin(admin.ModelAdmin):
    pass
