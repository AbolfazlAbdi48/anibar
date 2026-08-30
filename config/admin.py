from datetime import timedelta

from django.contrib import admin
from django.contrib.admin.apps import AdminConfig
from django.urls import reverse
from django.utils import timezone


class CustomAdminSite(admin.AdminSite):
    def get_app_list(self, request, app_label=None):
        # Fetch all apps registered globally (including Django auth, third-party packages, etc.)
        app_list = super().get_app_list(request, app_label)

        account_app = None
        shipment_app = None

        # Find our target apps
        for app in app_list:
            if app['app_label'] == 'account':
                account_app = app
            elif app['app_label'] == 'shipment_module':
                shipment_app = app

        if shipment_app and account_app:
            # Filter out 'Shipment' and keep other models (POL, POD, Terms, etc.)
            filtered_shipment_models = [
                model for model in shipment_app['models']
                if model.get('object_name') != 'Shipment'
            ]

            # Extend account models with the filtered list
            account_app['models'].extend(filtered_shipment_models)

        # Compute dynamic date range for today's filter
        today = timezone.localdate()
        tomorrow = today + timedelta(days=1)

        today_str = today.strftime('%Y-%m-%d')
        tomorrow_str = tomorrow.strftime('%Y-%m-%d')

        # 2. Custom shipment links
        custom_shipment_links = [
            {
                'name': 'All Aerial Shipments',
                'object_name': 'all_shipments',
                'admin_url': reverse('admin:shipment_module_shipment_changelist'),
            },
            {
                'name': 'Confirmed Aerial Shipments',
                'object_name': 'confirmed_shipments',
                'admin_url': reverse('admin:shipment_module_shipment_changelist') + '?confirmed__exact=1',
                'view_only': True,
            },
            {
                'name': 'Force Aerial Shipments',
                'object_name': 'force_shipments',
                'admin_url': reverse('admin:shipment_module_shipment_changelist') + '?priority__exact=red',
                'view_only': True,
            },
            {
                'name': "Today's ETA Shipments",
                'object_name': 'today_eta_shipments',
                'admin_url': (
                        reverse('admin:shipment_module_shipment_changelist')
                        + f'?eta__gte={today_str}&eta__lt={tomorrow_str}'
                ),
                'view_only': True,
            },
        ]

        if shipment_app:
            shipment_app['models'] = custom_shipment_links
        else:
            app_list.insert(0, {
                'name': 'Aerial Shipments',
                'app_label': 'shipment',
                'app_url': '#',
                'has_module_perms': True,
                'models': custom_shipment_links,
            })

        return app_list


# Custom AdminConfig that points to our CustomAdminSite class
class CustomAdminConfig(AdminConfig):
    default_site = 'config.admin.CustomAdminSite'
