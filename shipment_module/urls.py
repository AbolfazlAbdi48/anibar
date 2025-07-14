from django.urls import path
from .views import InvoiceViewDetail, main_view

app_name = "shipment"
urlpatterns = [
    path("", main_view, name='main'),

    path("shipment/invoice/<pk>", InvoiceViewDetail.as_view(), name="invoice-detail")
]
