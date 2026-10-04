from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from .models import SeaShipment, Container, SeaPolList, SeaPodList, SeaCarrier


def _badge(text, color):
    return format_html(
        '<span style="padding:2px 8px; border-radius:10px; font-size:11px; '
        'color:#fff; background:{};">{}</span>',
        color, text
    )


class SeaContainerInline(admin.TabularInline):
    model = Container
    extra = 0
    fields = ("container_no", "container_type", "seal_no", "gw", "vol")
    show_change_link = True


@admin.register(SeaShipment)
class SeaShipmentAdmin(admin.ModelAdmin):
    # ------------------------------------------------------------------
    # List View
    # ------------------------------------------------------------------
    list_display = (
        "ref", "client", "mode", "pol_pod",
        "gw", "vol", "freight_term",
        "cfm_status", "invoice_status", "payment_status",
        "grand_total_usd", "created_at",
    )
    list_display_links = ("ref",)
    list_editable = ("mode", "freight_term")
    list_select_related = ("client", "pol", "pod", "term", "agent")

    list_filter = (
        "mode", "freight_term",
        "confirmed", "invoice_issued", "payment_done",
        ("pol", admin.RelatedOnlyFieldListFilter),
        ("pod", admin.RelatedOnlyFieldListFilter),
        ("term", admin.RelatedOnlyFieldListFilter),
    )

    search_fields = (
        "ref", "mbl_no", "hbl_no", "booking_no",
        "container_no", "client__name",
    )
    autocomplete_fields = (
        "client", "sp", "pol", "pod", "term", "agent", "hbl_shipper", "hbl_cnee")
    filter_horizontal = ("operators",)
    inlines = (SeaContainerInline,)
    save_on_top = True
    list_per_page = 25

    # ------------------------------------------------------------------
    # Form Layout - 3 major sections like the Air module
    # ------------------------------------------------------------------
    fieldsets = (
        ("Basic Details", {
            "fields": (
                "ref", "client", "sp",
                "pol", "pod",
                "mode", "term", "agent", "priority",
                "inq_replied", "confirmed", "cfm_date",
            ),
        }),
        ("Cargo Details", {
            "fields": (
                "mbl_no", "hbl_no", "booking_no", "carrier",
                "hbl_shipper", "hbl_cnee",
                "notify_party",
                "pcs",
                "gw", "vol",
                "atd", "eta",
            ),
        }),
        ("Invoices & Charges", {
            "classes": ("wide", "collapse"),
            "fields": (
                "freight_term", "currency",
                "ocean_freight", "thc_pol", "thc_pod",
                "pickup_inland", "customs_clearance",
                "do_fee", "transit_fee",
                "other_charges", "extra_charges",
                "total_usd", "grand_total_usd",
                "invoice_deadline", "invoice_issued", "payment_done",
                "operators",
            ),
        }),
    )

    readonly_fields = ("total_usd", "grand_total_usd", "created_at", "updated_at")

    actions = (
        "mark_confirmed",
        "mark_invoice_issued",
        "mark_payment_done",
    )

    # ------------------------------------------------------------------
    # List Display Helpers
    # ------------------------------------------------------------------
    @admin.display(description="P.O.L / P.O.D")
    def pol_pod(self, obj):
        pol = obj.pol
        pod = obj.pod
        if pol and pod:
            return format_html(
                '{} <span style="color: #999; margin: 0 4px; font-size: 11px;">▶</span> {}',
                pol,
                pod,
            )
        return "—"

    @admin.display(description="CFM")
    def cfm_status(self, obj):
        return _badge("CFM" if obj.confirmed else "N/A",
                      "#27ae60" if obj.confirmed else "#bbb")

    @admin.display(description="Invoice")
    def invoice_status(self, obj):
        return _badge("Issued" if obj.invoice_issued else "Pending",
                      "#4a90d9" if obj.invoice_issued else "#bbb")

    @admin.display(description="Payment")
    def payment_status(self, obj):
        return _badge("Paid" if obj.payment_done else "Due",
                      "#27ae60" if obj.payment_done else "#e74c3c")

    def view_on_site(self, obj):
        return reverse(
            f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change",
            args=(obj.pk,)
        )

    # ------------------------------------------------------------------
    # Actions
    # -----------------------------------------------      self.message_user(request, f"{updated} shipment(s) confirmed.")

    @admin.action(description="Mark selected as Invoice Issued")
    def mark_invoice_issued(self, request, queryset):
        updated = queryset.update(invoice_issued=True)
        self.message_user(request, f"{updated} shipment(s) invoiced.")

    @admin.action(description="Mark selected as Payment Done")
    def mark_payment_done(self, request, queryset):
        updated = queryset.update(payment_done=True)
        self.message_user(request, f"{updated} shipment(s) paid.")

    # ------------------------------------------------------------------
    # Permissions / Overrides
    # ------------------------------------------------------------------
    def has_delete_permission(self, request, obj=None):
        # Disallow deletion of paid shipments
        if obj and obj.payment_done:
            return False
        return super().has_delete_permission(request, obj)

    def save_model(self, request, obj, form, change):
        obj.calculate_totals()
        super().save_model(request, obj, form, change)


@admin.register(Container)
class ContainerAdmin(admin.ModelAdmin):
    list_display = ("container_no", "container_type", "seal_no", "shipment", "gw", "vol")
    list_select_related = ("shipment",)
    search_fields = ("container_no", "seal_no", "shipment__ref")
    list_filter = ("container_type",)


@admin.register(SeaPolList)
class SeaPolListAdmin(admin.ModelAdmin):
    list_display = ("data", "country_name", "country_abbr", "airport_abbr")
    search_fields = ("data", "country_name", "airport_abbr")
    ordering = ("data",)


@admin.register(SeaPodList)
class SeaPodListAdmin(admin.ModelAdmin):
    list_display = ("data", "country_name", "country_abbr", "airport_abbr")
    search_fields = ("data", "country_name", "airport_abbr")
    ordering = ("data",)


@admin.register(SeaCarrier)
class CarrierAdmin(admin.ModelAdmin):
    list_display = ("name", "abbreviation", "national_id", "description")
    search_fields = ("name", "abbreviation", "national_id", "description")
    ordering = ("name",)
