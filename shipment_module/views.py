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


class ManifestView(DetailView, LoginRequiredMixin):
    model = Shipment

    def render_to_response(self, context, **response_kwargs):
        shipment = self.get_object()
        lines = [
            self.build_voy_line(shipment),
            self.build_bol_line(shipment),
            self.build_ctr_line(shipment),
            self.build_con_line(shipment),
        ]

        # Join with exact quotes and commas
        content = "\n".join(['"' + '","'.join(map(str, line)) + '"' for line in lines])

        response = HttpResponse(content, content_type='text/plain; charset=utf-8')
        filename = f"Manifest_{shipment.ref or shipment.pk}_{shipment.hawb or 'unknown'}.txt"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    def build_voy_line(self, shipment):
        return [
            "VOY",
            self.get_national_id_consignee_master(shipment),
            self.get_national_id_carrier(shipment),
            "",  # 3
            "W50064",
            "IRIKA",
            "",  # 6
            "",  # 7
            "MFI",
            "1",
            "5"
        ]

    def build_bol_line(self, shipment):
        pol = shipment.pol.airport_abbr if shipment.pol and shipment.pol.airport_abbr else ""
        etd_str = shipment.etd.strftime("%d%b%Y").upper() if shipment.etd else ""

        return [
            "BOL",
            shipment.hawb or "",
            "10102122004",
            "10102122004",
            "7",
            pol,
            "IRIKA",
            "IRIKA",
            etd_str,
            "", "", "I", "S", "", "", "G", "N", "Y",
            "FCL/FCL",
            "", "", "", "", "9", "", "", "10", "11", "", "12", "13",
            "TEHRAN, IRAN", "", "", "", "", "", "", "", "", "", "NM",
            shipment.hscode or "",
            shipment.commodity or "",
            shipment.pcs or "",
            "PLT", "PLT",
            shipment.hawb or "BULK1234567",
            "1", "1", "0", "1",
            shipment.gw or "",
            "0", "0", "0", "0", "Y", "", ""
        ]

    def build_ctr_line(self, shipment):
        return [
            "CTR",
            shipment.hawb or "BULK1234567",
            "1", "1", "1"
        ]

    def build_con_line(self, shipment):
        return [
            "CON",
            "4048653A",
            "NM",
            shipment.commodity or "ELECTRIC TERMINAL",
            "N",
            shipment.hscode or "85369010",
            shipment.pcs or "8",
            "PLT", "PLT",
            shipment.pcs or "8",
            shipment.gw or "1535",
            shipment.vol or "18",
            "N", "", "", "0", "C", "D", "N", "0", "0", "C"
        ]

    # === Helpers ===
    def get_national_id_consignee_master(self, shipment):
        return getattr(shipment.cnee, 'national_id', '') if shipment.cnee else ''

    def get_national_id_carrier(self, shipment):
        return getattr(shipment.carrier, 'national_id', '') if shipment.carrier else ''