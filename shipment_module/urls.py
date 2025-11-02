from django.urls import path
from .views import InvoiceViewDetail, main_view, ManifestView

app_name = "shipment"
urlpatterns = [
    path("", main_view, name='main'),

    path("shipment/invoice/<pk>", InvoiceViewDetail.as_view(), name="invoice-detail"),
    path("shipment/manifest/<int:pk>/", ManifestView.as_view(), name="manifest-detail"),
]
