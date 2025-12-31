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
        flight_1, flight_2 = self.get_flights(shipment)
        
        return [
            "VOY",
            shipment.cnee.national_id or "",
            shipment.carrier.national_id or "",
            flight_1, #1?
            flight_2, #1?
            #2?
            self.format_date(shipment.eta) or "",
            "",
            "MFI",
            "1",
            shipment.manifest_no or "",
        ]

    # =========================
    # BOL
    # =========================
    def build_bol_line(self, shipment):

        return [
            "BOL",
            shipment.hawb or "",
            "10102122004", "10102122004",
            shipment.pol.airport_abbr or "",              
            shipment.pol.airport_abbr or "",
            #2?
            self.format_date(shipment.eta) or "",
            "",
            "I",
            "S",
            "", "",
            "G",
            "N","Y","FCL/FCL",
            shipment.pol.country_abbr or "",
            "","","","",
            shipment.mawb or "",
            "", "",
            shipment.shipper.name or "",
            shipment.pol.country_name or "",
            "",
            shipment.cnee.national_id or "",
            shipment.cnee or "",
            "","","","","","","","","","NM",
            shipment.hscode or "",
            shipment.commodity or "",
            shipment.pcs or "",
            "CTN",
            "CTN",
            "BULK1234567", #12?
            "1","1","0","1",
            shipment.gw or "",
            shipment.gw or "",
            "0","0","0","0","Y","",""
        ]

    # =========================
    # CTR
    # =========================
    def build_ctr_line(self, shipment):
        return [
            "CTR",
            "BULK1234567", #12?
            "1",
            "1",
            "1",
        ]

    # =========================
    # CON
    # =========================
    def build_con_line(self, shipment):
        return [
            "CON",
            shipment.manifest_no or "",
            "NM",
            shipment.commodity or "",
            "N",
            shipment.hscode or "",
            shipment.pcs or "",
            "CTN",
            "CTN",
            shipment.pcs or "",
            shipment.gw or "",
            shipment.vol or "",
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