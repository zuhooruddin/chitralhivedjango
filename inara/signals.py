import os

from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Order


def _get_order_alert_recipients():
    env_value = os.environ.get("ORDER_ALERT_EMAILS", "").strip()
    if env_value:
        return [email.strip() for email in env_value.split(",") if email.strip()]
    return [settings.EMAIL_HOST_USER]


@receiver(post_save, sender=Order)
def send_new_order_notification(sender, instance, created, **kwargs):
    if not created:
        return

    recipients = _get_order_alert_recipients()
    if not recipients:
        return

    subject = f"New Order Received: {instance.orderNo or instance.id}"
    body = (
        "A new order has been received.\n\n"
        f"Order ID: {instance.id}\n"
        f"Order No: {instance.orderNo}\n"
        f"Customer: {instance.custName or 'N/A'}\n"
        f"Email: {instance.custEmail or 'N/A'}\n"
        f"Phone: {instance.custPhone or 'N/A'}\n"
        f"City: {instance.custCity or 'N/A'}\n"
        f"Total Bill: {instance.totalBill}\n"
        f"Status: {instance.status}\n"
        f"Timestamp: {instance.timestamp}\n"
    )

    send_mail(
        subject=subject,
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipients,
        fail_silently=False,
    )
