from inara.models import Item,Category,CategoryItem
from django.http import JsonResponse
from rest_framework.response import Response
import json
import re
import os
from ecommerce_backend.settings import BASE_DIR
import requests
from unidecode import unidecode
from django.db import IntegrityError
import random
from datetime import datetime, timedelta
from celery.exceptions import Ignore
import environ
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
import logging
logger = logging.getLogger(__name__)

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
    isNewArrival    = None
    newArrivalTill  = None
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
        self.isNewArrival         = None
        self.newArrivalTill       = None
        # self.discount        = None
        self.status          = None

class RPOS7CategoryItem(object):	
    categoryId       = None
    itemId           = None
    level            = None
    

class RPOS7ItemSync(object):

    def syncItems(self):
        context = {}
        errorList = []
        r1=requests.get("https://722157.true-order.com/WebReporter/api/v1/items", headers={"X-Auth-Token":env('POS_AUTH_TOKEN')})
        if(r1.status_code==424):
            logger.info("POS is not Reachable in Schedule Item Sync.")
            raise Ignore
        jsonObj1 = r1.json()
        try:
            for iteration in range(1,jsonObj1['total_pages']+1):
                logger.info("Item Sync Page No: %s " %(str(iteration)))
                r=requests.get("https://722157.true-order.com/WebReporter/api/v1/items?page="+str(iteration), headers={"X-Auth-Token":env('POS_AUTH_TOKEN')})
                if(r.status_code==424):
                    logger.info("POS is not Reachable in Schedule Item Sync.")
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
                    if item['status'] == "R" and item['appliesOnline'] == 1:
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
                            itemObject           = Item.UpdateItem(obj.__dict__,item['itemId'])
                            
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
                            obj.isNewArrival = 1
                            init_time = datetime.now()
                            tillDate = init_time + timedelta(days = 7)
                            obj.newArrivalTill =  tillDate
                            itemObject       = Item.AddItem(obj.__dict__)
                            if(objCategoryItem1.categoryId):
                                CategoryItem.objects.create(categoryId=objCategoryItem1.categoryId,itemId=itemObject,level=0)
                            if(objCategoryItem2.categoryId):
                                CategoryItem.objects.create(categoryId=objCategoryItem2.categoryId,itemId=itemObject,level=1)

                            
                        except Exception as error:
                            print("Exception in items gofrugle " + str(error))
                            errorList.append({"Error":'Item ID = '+str(item['itemId'])+' item Name = '+item['itemName']+', Error: '+str(error)})
                            pass

        except Exception as e:
            print("Exception in SyncItem - RPOS7: " + str(e))
            errorList.append({"Error":'Sync Process Error : '+str(e)})
            pass
        
        if errorList:
            errorResponse = ', '.join(d['Error'] for d in errorList)
            logger.error("Exception in Item Sync: %s " %(str(errorResponse)))

        return JsonResponse({'errorcode':'success'})