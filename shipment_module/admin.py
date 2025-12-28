from django.contrib import admin
from django.urls import reverse
from import_export.admin import ImportExportModelAdmin
from django.utils.html import format_html


from .models import (
    Shipment,
    PolList,
    PodList,
    TermList,
    Console,
    Charge,
    ShipmentComment,
)
from .resources import ShipmentModelResource


# -------------------------------
# Inline models
# -------------------------------
class ChargeInline(admin.TabularInline):
    model = Charge
    extra = 0
    verbose_name = "Charge"
    verbose_name_plural = "Charges"


class CommentInline(admin.TabularInline):
    model = ShipmentComment
    extra = 1
    readonly_fields = ("author_name", "created_at")
    fields = ("text", "author_name", "created_at")
    can_delete = True



# -------------------------------
# Shipment Admin
# -------------------------------
@admin.register(Shipment)
class ShipmentAdmin(ImportExportModelAdmin):
    resource_class = ShipmentModelResource
    filter_horizontal = ("operators",)
    inlines = [ChargeInline, CommentInline]
    autocomplete_fields = ['shipper', 'hawb_shipper', 'cnee', 'hawb_cnee']

    list_display = (
        "ref",
        "colored_priority_badge",
        "client",
        "sp",
        "inq_replied",
        "confirmed",
        "confirm_date",
        "carrier",
        "agent",
        "console",
        "mawb",
        "hawb",
        "etd",
        "eta",
        "transit_time",
        "pol",
        "pod",
        "term",
        "invoice_deadline",
        "extra_charges",
        "manifest_link",
    )

    # only confirmed is editable in list
    list_editable = ("confirmed",)

    list_filter = (
        "confirmed",
        "inq_replied",
        "client",
        "carrier",
        "agent",
        "console",
        "pol",
        "pod",
        "term",
        "priority",
        "eta",
        "sp",
    )

    search_fields = (
        "ref",
        "client__name",
        "sp__username",
        "mawb",
        "hawb",
        "shipper__name",
        "cnee__name",
        "hawb_shipper__name",
        "hawb_cnee__name",
        "carrier__name",
    )

    search_help_text = "Search by Ref, Client, S/P, MAWB, HAWB, Shipper, Consignee, or Carrier"
    list_per_page = 50
    readonly_fields = ("transit_time", "manifest_download_link")

    fieldsets = (
        ("1. Basic Details", {
            "fields": (
                "ref", "client", "sp", "pol", "pod",
                "priority", "agent", "mode", "first_gw", "first_cw", "term","invoice_deadline"
            )
        }),
        ("2. Cargo Details", {
            "fields": (
                "inq_replied", "confirmed", "confirm_date", "commodity", "pcs", "gw","cw", "vol", "currency",
                "via", "first_master", "first_house", "etdw", "etd", "eta",
                "transit_time", "console", "mawb", "hawb",
                 "manifest_no", "carrier", "shipper", "cnee", "hawb_shipper", "hawb_cnee", "operators", "extra_charges", "manifest_download_link"
                
            )
        }),
    )

    

    # store current request for comment inline to use
    def get_form(self, request, obj=None, **kwargs):
        self._current_request = request
        return super().get_form(request, obj, **kwargs)

    # helper display
    def colored_priority_badge(self, obj):
        colors = {"green": "#6cc24a", "yellow": "#ffd43b", "red": "#ff4d4f"}
        color = colors.get(obj.priority, "#ddd")
        return format_html(
            '<span style="padding:4px 8px;border-radius:5px;background:{};color:#fff;">{}</span>',
            color,
            obj.get_priority_display(),
        )
    colored_priority_badge.short_description = "Priority"

    # prefill S/P
    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        if not request.user.is_anonymous:
            initial["sp"] = request.user.pk
        return initial

    def save_formset(self, request, form, formset, change):
        """Attach current user to comments before saving."""
        instances = formset.save(commit=False)
        for obj in instances:
            if isinstance(obj, ShipmentComment):
                obj._current_user = request.user  # attach the logged-in user
            obj.save()
        formset.save_m2m()

    # === MANIFEST BUTTON (LIST) - COLORED ===
    # === 1. MANIFEST HYPERLINK IN LIST (no color, no button) ===
    def manifest_link(self, obj):
        if not obj.pk:
            return "-"
        url = reverse("shipment:manifest-detail", args=[obj.pk])
        return format_html(
        '<a href="{}" download '
        'style="color:#0073aa; font-weight:bold; text-decoration:underline;">'
        'Download Manifest'
        '</a>',
        url
        )
    manifest_link.short_description = "Manifest"

    # === 2. DOWNLOAD BUTTON ON EDIT PAGE ===
    def manifest_download_link(self, obj):
        if not obj.pk:
            return "Save first to generate manifest."
        url = reverse("shipment:manifest-detail", args=[obj.pk])
        return format_html(
            '<div style="margin-top:20px;">'
            '<a href="{}" download '
            'style="background:#44b78b;color:white;padding:10px 16px;border-radius:5px;text-decoration:none;font-weight:bold;">'
            'Download Manifest.txt'
            '</a>'
            '</div>',
            url
        )
    manifest_download_link.short_description = ""


# -------------------------------
# Supporting Models
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


@admin.register(Console)
class ConsoleAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "created_at")
    search_fields = ("code",)
    ordering = ("-created_at",)
