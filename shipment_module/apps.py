from django.apps import AppConfig


class ShipmentModuleConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "shipment_module"
    verbose_name = "1. Shipment Module"

class ShipmentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shipment_module'
    verbose_name = "1. Shipment Module"

    def ready(self):
        import shipment_module.signals
        print("Signals loaded via AppConfig.ready()")