# feedback/tasks.py

from time import sleep
from celery import shared_task
from . import views

@shared_task()
def sync_category():
    """Sends an email when the feedback form has been submitted."""
    sleep(20)  # Simulate expensive operation(s) that freeze Django
    views.syncCategories()
    