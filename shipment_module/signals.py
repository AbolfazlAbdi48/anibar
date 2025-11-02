# shipment_module/signals.py
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone
from django.conf import settings
from .utils import send_sms

@receiver(user_logged_in)
def send_login_sms(sender, request, user, **kwargs):
    login_time = timezone.localtime(timezone.now()).strftime("%Y-%m-%d %H:%M:%S")
    message = f"Admin login detected:\nUser: {user.username}\nTime: {login_time}"

    if user.username:
        send_sms(user.username, message)

    manager_phone = getattr(settings, "MANAGER_PHONE", None)
    if manager_phone:
        send_sms(manager_phone, message)