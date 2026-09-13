# shipment/admin.py - Sea Freight Module
# ------------------------------------------------------------------
# Assumptions:
#  - Shared models live in app "account": Client, SP, Pol, Pod, Term,
#    Console, Agent, Operator
#  - If any shared model has a different class name in your project,
#    just update the "to=" references below.
# ------------------------------------------------------------------

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from .models import SeaShipment, Container


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
        "ref", "client", "mode", "pol_pod", "vessel_voyage",
        "gw", "vol", "release_badge", "freight_term",
        "cfm_status", "invoice_status", "payment_status",
        "grand_total_usd", "created_at",
    )
    list_display_links = ("ref",)
    list_editable = ("mode", "freight_term")
    list_select_related = ("client", "pol", "pod", "term", "agent")

    list_filter = (
        "mode", "movement", "bl_release", "freight_term",
        "confirmed", "invoice_issued", "payment_done",
        ("pol", admin.RelatedOnlyFieldListFilter),
        ("pod", admin.RelatedOnlyFieldListFilter),
        ("term", admin.RelatedOnlyFieldListFilter),
    )

    search_fields = (
        "ref", "mbl_no", "hbl_no", "booking_no", "vessel_name",
        "voyage_no", "container_no", "client__name",
        "hbl_shipper", "hbl_cnee", "mbl_shipper", "mbl_cnee",
    )
    autocomplete_fields = ("client", "sp", "pol", "pod", "term", "console", "agent")
    filter_horizontal = ("operators",)
    inlines = (SeaContainerInline,)
    date_hierarchy = "etd"
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
                "place_of_receipt", "final_destination",
                "mode", "movement", "term",
                "console", "agent", "priority",
                "bl_release", "booking_no",
                "inq_replied", "confirmed", "cfm_date",
            ),
        }),
        ("Cargo & Vessel Details", {
            "fields": (
                "vessel_name", "voyage_no",
                "mbl_no", "hbl_no", "manifest_no",
                "mbl_shipper", "mbl_cnee",
                "hbl_shipper", "hbl_cnee",
                "notify_party", "delivery_agent",
                "container_type",
                "pcs", "marks", "commodity", "hscode",
                "gw", "vol", "cw",
                "etd", "atd", "eta", "ata",
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
        "mark_telex_release",
    )

    # ------------------------------------------------------------------
    # List Display Helpers
    # ------------------------------------------------------------------
    @admin.display(description="P.O.L / P.O.D")
    def pol_pod(self, obj):
        pol = obj.pol
        pod = obj.pod
        if pol and pod:
            return f"{pol} <i style='color:#999;'>▶</i> {pod}"
        return "—"

    @admin.display(description="Vessel / Voyage")
    def vessel_voyage(self, obj):
        if obj.vessel_name:
            return f"{obj.vessel_name} / {obj.voyage_no}"
        return "—"

    @admin.display(description="Release")
    def release_badge(self, obj):
        labels = {
            "original": ("Original B/L", "#4a90d9"),
            "telex": ("Telex Release", "#f39c12"),
            "waybill": ("Sea Waybill", "#27ae60"),
        }
        text, color = labels.get(obj.bl_release, ("—", "#bbb"))
        return _badge(text, color)

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

    @admin.action(description="Mark selected as Telex Release")
    def mark_telex_release(self, request, queryset):
        updated = queryset.update(bl_release="telex")
        self.message_user(request, f"{updated} shipment(s) set to Telex Release.")

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
