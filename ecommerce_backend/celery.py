import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_backend.settings')
import django
django.setup()
from celery import Celery
# import logging
import logging,os
from . import settings
from celery import shared_task
from celery.schedules import crontab
from inara import views
from datetime import datetime, timedelta
from .views import cancel_unpaid_orders_view

######## END ##############

logfmt = logging.Formatter("%(asctime)s %(levelname)s: %(name)s( %(module)s.%(funcName)s():%(lineno)d )- %(message)s")
celeryLogHandler = logging.handlers.TimedRotatingFileHandler(str(os.path.join(settings.LOGS_DIR, "celery.log")), when='midnight',backupCount=0, encoding=None, delay=False, utc=True)
celeryLogHandler.setFormatter(logfmt)
celeryLogger = logging.getLogger(__name__)
celeryLogger.setLevel(10)
celeryLogger.addHandler(celeryLogHandler)
celeryLogger.info('Logging enabled')

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_backend.settings')
# logger = logging.getLogger(__name__)
# django.setup()
app = Celery('ecommerce_backend')
app.config_from_object('ecommerce_backend.settings')
# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
# app.config_from_object('django.conf:settings')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(minute=10, hour=19),
        # 30.0,
        sync_categories.s(),
    )
    sender.add_periodic_task(
        crontab(minute=52, hour=19),
        sync_items.s(),
    )
    sender.add_periodic_task(
        crontab(minute=0, hour="*/12"),
        SyncObjectStorageItemImages.s(),
    )
    sender.add_periodic_task(
        crontab(minute="0", hour="12"),
        DynamicSiteMapGeneratorTask.s(),
        )
    sender.add_periodic_task(
        crontab(minute="10", hour="12"),
        ResetIsNewArrivalTask.s(),
    )
    sender.add_periodic_task(
        crontab(minute="*/30"), 
        CancelOrder.s(),  
    )

@app.task
def debug_task(message):
    print(f'Request: {message}')
    celeryLogger.info("%s" %(message))
    celeryLogger.info("%s" %('Default Message'))
    views.syncCategories
    print(f'Request: syncCategory called')
    celeryLogger.info("%s" %('syncCategory called'))

@app.task
def sync_categories():
    context = {'Key':'success'}
    category_module_name = 'inara.core.middlewares.externalPOS.Gofrugal_RPOS7.category'
    category_class_name = 'RPOS7CategorySync'
    className = views.class_for_name(category_module_name, category_class_name)
    syncObj = className()
    # extPos = request.pos
    extPos = 'Gofrugal_RPOS7'
    syncObj.syncCategories()
    celeryLogger.info("%s" %('Sync Categories'))
    print(f'Request: sync Categories')

@app.task
def sync_items():
    # context = {'Key':'success'}
    item_module_name = 'inara.core.middlewares.externalPOS.Gofrugal_RPOS7.item'
    item_class_name = 'RPOS7ItemSync'
    className = views.class_for_name(item_module_name, item_class_name)
    syncObj = className()
    # extPos = request.pos
    # extPos = 'Gofrugal_RPOS7'
    syncObj.syncItems()


    
@app.task
def SyncObjectStorageItemImages():
    celeryLogger.info("%s" %('Sync Object Storage Item Images'))
    views.SyncObjectStorageItemImages()
    celeryLogger.info("%s" %('Complete -- Sync Object Storage Item Images'))
    
@app.task
def DynamicSiteMapGeneratorTask():
    celeryLogger.info("%s" %('Dynamic Sitemap Generator Task initiated'))
    views.DynamicSiteMapGenerator()
    celeryLogger.info("%s" %('Complete -- Dynamic SiteMap Generator Task'))
@app.task    
def ResetIsNewArrivalTask():
    celeryLogger.info("%s" %('ResetIsNewArrivaltask initiated'))
    views.ResetIsNewArrivalTask()
    celeryLogger.info("%s" %('Complete -- ResetIsNewArrivaltask Task'))

@shared_task
def CancelOrder():
    try:
        celeryLogger.info("Cancel order initiated")
        response = views.cancelUnpaidOrder()
        celeryLogger.info("Complete -- Cancel order")
        return response  
    except Exception as e:
        celeryLogger.error(f"Error cancelling orders: {str(e)}")
