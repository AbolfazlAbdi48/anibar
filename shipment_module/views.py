from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Shipment

# Create your views here.
def main_view(request):
    return redirect('/admin/')


class InvoiceViewDetail(DetailView, LoginRequiredMixin):
    model = Shipment
    template_name = 'shipment/invoice_detail.html'


class ManifestView(LoginRequiredMixin, DetailView):
    model = Shipment

    def render_to_response(self, context, **kwargs):
        shipment = self.get_object()

        lines = [
            self.build_voy_line(shipment),
            self.build_bol_line(shipment),
            self.build_ctr_line(shipment),
            self.build_con_line(shipment),
        ]

        # exact CSV-style output with quotes
        content = "\n".join(
            ['"' + '","'.join(str(v or "") for v in line) + '"' for line in lines]
        )

        response = HttpResponse(content, content_type="text/plain; charset=utf-8")
        response["Content-Disposition"] = (
            f'attachment; filename="Manifest_{shipment.ref or shipment.pk}.txt"'
        )
        return response

    # =========================
    # VOY
    # =========================
    def build_voy_line(self, shipment):
        # 1) national id consignee master
        cnee_national_id = shipment.cnee.national_id if shipment.cnee else ""

        # 2) national id carrier
        carrier_national_id = shipment.carrier.national_id if shipment.carrier else ""

        # 3–4) two flights (derived, not DB fields)
        flight_1, flight_2 = self.get_flights(shipment)

        # 5) manifest number
        manifest_no = shipment.manifest_no or ""

        return [
            "VOY",
            cnee_national_id,
            carrier_national_id,
            flight_1,
            flight_2,
            "IRIKA",  # operator (fixed per sample)
            self.format_date(shipment.eta),  # ETA (corrected)
            "",
            "MFI",
            "1",
            manifest_no,
        ]

    # =========================
    # BOL
    # =========================
    def build_bol_line(self, shipment):
        pol_airport = shipment.pol.airport_abbr if shipment.pol else ""
        pol_country_abbr = shipment.pol.country_abbr if shipment.pol else ""
        pol_country_name = shipment.pol.country_name if shipment.pol else ""

        hawb = shipment.hawb or ""
        mawb = shipment.mawb or ""

        shipper_name = shipment.hawb_shipper.name if shipment.hawb_shipper else ""
        cnee_national_id = shipment.hawb_cnee.national_id if shipment.hawb_cnee else ""
        cnee_name_address = (
            f"{shipment.hawb_cnee.name} {shipment.hawb_cnee.address}"
            if shipment.hawb_cnee else ""
        )

        return [
            "BOL",
            hawb,                     # 6 HAWB
            "", "",
            "7",
            pol_airport,              # 7 POL airline
            pol_airport,              # 5 POL twice
            pol_country_abbr,         # 8 country abbr
            self.format_date(shipment.eta),  # 3 ETA fixed
            "I",
            "S",
            "", "",
            "G",
            "N",
            mawb,                     # 9 MAWB
            "", "",                   # 8 two empty cells
            shipper_name,             # 10 shipper house
            pol_country_name,         # 11 country name
            "",
            cnee_national_id,         # 12 cnee national id
            cnee_name_address,        # 13 cnee name + address
            shipment.hscode or "",    # 14 HS code
            shipment.commodity or "", # 15 commodity
        ]

    # =========================
    # CTR
    # =========================
    def build_ctr_line(self, shipment):
        return [
            "CTR",
            "BULK1234567",             # 12 fixed house number
            shipment.pcs or "",
            shipment.pcs or "",
            shipment.pcs or "",
        ]

    # =========================
    # CON
    # =========================
    def build_con_line(self, shipment):
        return [
            "CON",
            shipment.ref or "",
            "NM",
            shipment.commodity or "",
            "N",
            shipment.hscode or "",
            shipment.pcs or "",
            "CTN",
            "CTN",
            shipment.pcs or "",
            shipment.gw or "",         # 13 weight (1)
            shipment.gw or "",         # 13 weight (2)
            shipment.vol or "",        # 18 volume
            "N",
            "",
            "",
            "0",
            "C",
            "D",
            "N",
            "0",
            "0",
            "C",
        ]

    # =========================
    # Helpers
    # =========================
    def get_flights(self, shipment):
        """
        Flights are derived, not stored.
        Adjust logic later if needed.
        """
        if shipment.mode and shipment.mode.startswith("air"):
            return ("EK9873", "EK9873")
        return ("", "")

    def format_date(self, date_obj):
        if not date_obj:
            return ""
        return date_obj.strftime("%d%b%Y").upper()