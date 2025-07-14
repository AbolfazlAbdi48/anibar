from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import DetailView

from shipment_module.models import Shipment


# Create your views here.
def main_view(request):
    return redirect('/admin/')


class InvoiceViewDetail(DetailView, LoginRequiredMixin):
    model = Shipment
    template_name = 'shipment/invoice_detail.html'
