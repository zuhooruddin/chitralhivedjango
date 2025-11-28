###### OnClick Fetch Categories imoports #########
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_backend.settings')
import django
django.setup()
from celery import Celery
# import logging
import logging,os
from . import settings
# from celery import shared_task
# from celery.schedules import crontab
logger = logging.getLogger(__name__)
import requests
from django.http import JsonResponse
from inara.models import Item,Category,TaskProgress,task_canceled,task_stopped
from unidecode import unidecode
import re
import random
# from celery.schedules import crontab
# from inara import views
# from inara.models import *
from celery.result import AsyncResult
import datetime
from celery.exceptions import Ignore
# from celery.task.control import revoke

import environ
env = environ.Env()
environ.Env.read_env()
######## END ##############

logfmt = logging.Formatter("%(asctime)s %(levelname)s: %(name)s( %(module)s.%(funcName)s():%(lineno)d )- %(message)s")
celeryLogHandler = logging.handlers.TimedRotatingFileHandler(str(os.path.join(settings.LOGS_DIR, "celery.log")), when='midnight',backupCount=0, encoding=None, delay=False, utc=True)
celeryLogHandler.setFormatter(logfmt)
celeryLogger = logging.getLogger(__name__)
celeryLogger.setLevel(10)
celeryLogger.addHandler(celeryLogHandler)
celeryLogger.info('Logging enabled Tasks')

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
# app.autodiscover_tasks()


def checkIfTaskCancelled(msg):
    if task_canceled():
        task_stopped()
        if(TaskProgress.objects.filter(syncType="ITEM_SYNC",status="PROGRESS").exists()):
            pass
        else:
            logger.info("Sync Item Process Stopped by user: Page No: %s " %(str(msg)))
            raise Ignore

################################# OnClick fetch categories #######################################
class RPOS7Category(object):	
    extPosId        = None
    extPosParentId  = None
    parentId        = None
    name            = None
    catName         = None
    slug            = None
    description     = None
    appliesOnline   = None
    syncTs          = None
    lovSequence     = None
    status          = None
    
    def reset(self):
        self.extPosId       = None
        self.extPosParentId = None
        self.name           = None
        self.catName        = None
        self.slug           = None
        self.description    = None
        self.appliesOnline  = None
        self.syncTs         = None
        self.lovSequence    = None
        self.status         = None

@app.task(name="sync_categories_click")
def sync_categories_click():
    context = {}
    errorList = []
    r=requests.get("https://722157.true-order.com/WebReporter/api/v1/categories", headers={"X-Auth-Token":env('POS_AUTH_TOKEN')})
    if(r.status_code==424):
        TaskProgress.objects.filter(syncType="CATEGORY_SYNC",status="PROGRESS").update(cancelTask=True,status="STOPPED",statusReason="Pos is unreachable")
        logger.info("POS is unreachable.")
        raise Ignore
    json_data = r.json()
    try:
        sync_categories_click.update_state(state='PROGRESS', meta={'progress': 0})
        # TaskProgress.objects.filter(syncType="CATEGORY_SYNC",status="PROGRESS").update(status="PROGRESS")
        for categories in json_data['categories']:
            if (categories['catName'] == 'Cat1') or (categories['catName'] == 'Cat2'):
                # mapping_dict contains sync fields (update/create) from external pos
                for value in categories['categoryValues']:
                    obj = RPOS7Category()
                    text = unidecode(value['categoryValueName']).lower()
                    catSlug = re.sub(r'[\W_]+', '-', text)
                    if value['appliesOnline'] == 1:
                        status = Category.INACTIVE
                        if value['catStatus'] == "Y":
                            status = Category.ACTIVE
                        if Category.objects.filter(extPosId=value['categoryValueId']).exists():
                            obj.extPosParentId  = value['parentId']
                            obj.name            = value['categoryValueName']
                            obj.catName         = value['catName']
                            obj.description     = value['description']
                            obj.appliesOnline   = value['appliesOnline']
                            obj.syncTs          = value['syncTs']
                            obj.lovSequence     = value['lovSequence']
                            obj.status          = status
                            try:
                                catObject           = Category.UpdateCategory(obj.__dict__,value['categoryValueId'])
                            except Exception as error:
                                # exception = {"ErrorCode": error_codes.INTERNAL_SERVER_ERROR, "ErrorMsg": error_codes.INTERNAL_SERVER_ERROR_MSG,}
                                print("Exception in OnClick category gofrugle " + str(error))
                                errorList.append({"Error":str(error)})
                                pass
                        else:
                            # Category.AddCategory(value['categoryValueId'], value['parentId'], value['categoryValueName'], value['description'], value['appliesOnline'], value['syncTs'], value['lovSequence'], status,Category.EXTERNAL)
                            slugExists = True
                            while(slugExists):
                                if Category.objects.filter(slug=catSlug).exists():
                                    catSlug = catSlug+str(random.randint(0,9))
                                else:
                                    slugExists=False
                            obj.extPosId        = value['categoryValueId']
                            obj.extPosParentId  = value['parentId']
                            obj.name            = value['categoryValueName']
                            obj.catName         = value['catName']
                            obj.slug            = catSlug
                            obj.description     = value['description']
                            obj.appliesOnline   = value['appliesOnline']
                            obj.syncTs          = value['syncTs']
                            obj.lovSequence     = value['lovSequence']
                            obj.status          = status
                            try:
                                catObject           = Category.AddCategory(obj.__dict__)
                            except Exception as error:
                                print("Exception in OnClick category gofrugle " + str(error))
                                errorList.append({"Error":str(error)})
                                pass

                            if catObject.extPosParentId == 0:
                                pass
                            else:
                                posObject       = Category.objects.get(extPosId=catObject.extPosParentId)
                                Category.objects.filter(id=catObject.pk).update(parentId=posObject.pk)
        currentTime = datetime.datetime.now()  
        TaskProgress.objects.filter(syncType="CATEGORY_SYNC",status="PROGRESS").update(progress=100,completionTime=currentTime,status="COMPLETED")

    except Exception as e:
        print("Exception in OnClick SyncCategory - RPOS7: " + str(e))
        if(TaskProgress.objects.filter(syncType="CATEGORY_SYNC",status="PROGRESS").exists()):
                TaskProgress.objects.filter(syncType="CATEGORY_SYNC",status="PROGRESS").update(status="STOPPED",statusReason="Exception Occured")
        errorList.append({"Error":str(error)})
        pass
    if errorList:
        errorResponse = ', '.join(d['Error'] for d in errorList)
        logger.error("Exception in OnClick Category Sync: %s " %(str(errorResponse)))

########################## onClick Categories END ####################################

########################## onClick Items #####################################

class RPOS7Item(object):	
    extPosId        = None
    name            = None
    slug            = None
    sku             = None
    image           = None
    description     = None
    appliesOnline   = None
    weightGrams     = None
    manufacturer    = None
    length          = None
    height          = None
    weight          = None
    width           = None
    stock           = None
    mrp             = None
    salePrice       = None
    extTimestamp    = None
    author          = None
    isbn            = None
    aliasCode       = None
    # discount        = None
    status          = None
    
    def reset(self):
        self.extPosId        = None
        self.name            = None
        self.slug            = None
        self.sku             = None
        self.image           = None
        self.description     = None
        self.appliesOnline   = None
        self.weightGrams     = None
        self.manufacturer    = None
        self.length          = None
        self.height          = None
        self.weight          = None
        self.width           = None
        self.stock           = None
        self.mrp             = None
        self.salePrice       = None
        self.extTimestamp    = None
        self.author          = None
        self.isbn            = None
        self.aliasCode       = None
        # self.discount        = None
        self.status          = None

class RPOS7CategoryItem(object):	
    categoryId       = None
    itemId           = None
    level            = None

@app.task(name="sync_items_click")
def sync_items_click():
        context = {}
        errorList = []
        r1=requests.get("https://722157.true-order.com/WebReporter/api/v1/items",timeout=5, headers={"X-Auth-Token":env('POS_AUTH_TOKEN')})
        if(r1.status_code==424):
            TaskProgress.objects.filter(syncType="ITEM_SYNC",status="PROGRESS").update(cancelTask=True,status="STOPPED",statusReason="Pos is unreachable")
            logger.info("POS is not Reachable.")
            raise Ignore
        jsonObj1 = r1.json()
        try:
            sync_items_click.update_state(state='PROGRESS', meta={'progress': 0})
            try:
                checkProgressState = TaskProgress.objects.get(syncType="ITEM_SYNC",status="PROGRESS")
            except TaskProgress.DoesNotExist:
                raise Ignore
            TaskProgress.objects.filter(syncType="ITEM_SYNC",status="PROGRESS").update(total=jsonObj1['total_pages'])
            checkIfTaskCancelled("Before Sync Process Starts")
            for iteration in range(1,jsonObj1['total_pages']+1):
                checkIfTaskCancelled(iteration)
                logger.info("Item Sync Page No: %s " %(str(iteration)))
                r=requests.get("https://722157.true-order.com/WebReporter/api/v1/items?page="+str(iteration), headers={"X-Auth-Token":env('POS_AUTH_TOKEN')})
                if(r1.status_code==424):
                    TaskProgress.objects.filter(syncType="CATEGORY_SYNC",status="PROGRESS").update(cancelTask=True,status="STOPPED",statusReason="POS is unreachable")
                    logger.info("POS is not Reachable.")
                    raise Ignore
                jsonObj = r.json()
                for item in jsonObj['items']:
                    # if item['appliesOnline'] == 1:
                    obj = RPOS7Item()
                    objCategoryItem1 = RPOS7CategoryItem()
                    objCategoryItem2 = RPOS7CategoryItem()

                    text = unidecode(item['itemName']).lower()
                    itemSlug = re.sub(r'[\W_]+', '-', text)
                    
                    status = Item.INACTIVE
                    if item['status'] == "R":
                        status = Item.ACTIVE

                    obj.name            = item['itemName']
                    obj.sku             = item['itemId']
                    obj.description     = item['detailedDescription']
                    obj.weightGrams     = item['weightGrams']
                    obj.appliesOnline   = item['appliesOnline']
                    obj.manufacturer    = item['manufacturer']
                    obj.length          = item['length']
                    obj.height          = item['height']
                    obj.weight          = item['weight']
                    obj.width           = item['width']
                    obj.aliasCode       = item['itemId']
                    obj.status          = status
                    
                    for value in item['stock']:
                        obj.stock       = value['stock']
                        obj.mrp         = value['mrp']
                        obj.salePrice   = value['salePrice']
                        obj.author      = value['others'].split('author":"')[1].split('"')[0].strip()
                        obj.isbn        = value['others'].split('isbn":"')[1].split('"')[0].strip()
                        if value['Cat1']:
                            try:
                                objCat1 = Category.objects.get(name=value['Cat1'], catName="Cat1")
                                objCategoryItem1.categoryId = objCat1
                            except Exception as error:
                                print("Exception in Cat 1 gofrugle " + str(error))
                                errorList.append({"Error":'Item ID = '+str(item['itemId'])+' item Name = '+item['itemName']+', Error: '+str(error)})
                                pass
                        if value['Cat2']:
                            try:
                                objCat2 = Category.objects.get(name=value['Cat2'], catName="Cat2")
                                objCategoryItem2.categoryId = objCat2

                            except Exception as error:
                                print("Exception in Cat 2 gofrugle " + str(error))
                                errorList.append({"Error":'Item ID = '+str(item['itemId'])+' item Name = '+item['itemName']+', Error: '+str(error)})
                                pass

                    if Item.objects.filter(extPosId=item['itemId']).exists():
                        # pass
                        try:
                            itemObject = Item.UpdateItem(obj.__dict__,item['itemId'])

                        except Exception as error:
                            print("Exception in if items gofrugle " + str(error))
                            errorList.append({"Error":'Item ID = '+str(item['itemId'])+' item Name = '+item['itemName']+', Error: '+str(error)})
                            pass
                    else:
                        slugExists = True
                        while(slugExists):
                            if Item.objects.filter(slug=itemSlug).exists():
                                itemSlug = itemSlug+str(random.randint(0,9))
                            else:
                                slugExists=False
                                
                        obj.extPosId        = item['itemId']
                        obj.slug            = itemSlug
                        try:
                            itemObject           = Item.AddItem(obj.__dict__)
                            if(objCategoryItem1.categoryId):
                                CategoryItem.objects.create(categoryId=objCategoryItem1.categoryId,itemId=itemObject,level=0)
                            if(objCategoryItem2.categoryId):
                                CategoryItem.objects.create(categoryId=objCategoryItem2.categoryId,itemId=itemObject,level=1)

                        except Exception as error:
                            print("Exception in items gofrugle " + str(error))
                            errorList.append({"Error":'Item ID = '+str(item['itemId'])+' item Name = '+item['itemName']+', Error: '+str(error)})
                            pass
            # sync_items_click.update_state(state='PROGRESS', meta={'progress': 0})
                TaskProgress.objects.filter(syncType="ITEM_SYNC",status="PROGRESS").update(progress=iteration)
            currentTime = datetime.datetime.now()  
            TaskProgress.objects.filter(syncType="ITEM_SYNC",status="PROGRESS").update(completionTime=currentTime,status="COMPLETED")
        except Exception as e:
            print("Exception in SyncItem - RPOS7: " + str(e))
            if(TaskProgress.objects.filter(syncType="ITEM_SYNC",cancelTask=True,status="CANCELLED").exists()):
                TaskProgress.objects.filter(syncType="ITEM_SYNC",cancelTask=True,status="CANCELLED").update(status="STOPPED",statusReason="Exception Occured")
            errorList.append({"Error":'Sync Process Error : '+str(e)})
            pass
        
        if errorList:
            errorResponse = ', '.join(d['Error'] for d in errorList)
            logger.error("Exception in Item Sync: %s " %(str(errorResponse)))

###################################### onClick Items END #################################


def get_task_status(task_id):
    task = AsyncResult(task_id, app=app)
    status = task.status
    progress = 0 
    if status == 'SUCCESS':
        progress = 100
    elif status == 'FAILURE':
        progress = 0
    elif status == 'PROGRESS':
        progress = task.info['progress']
    return {'status': status, 'progress': progress}

