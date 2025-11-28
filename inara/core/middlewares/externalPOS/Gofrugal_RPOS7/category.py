from inara.models import Category
from django.http import JsonResponse
from rest_framework.response import Response
import json
import re
import os
from ecommerce_backend.settings import BASE_DIR
from unidecode import unidecode
from django.db import IntegrityError
import requests
import random
from inara.core import error_codes
from celery.exceptions import Ignore
import environ
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
import logging
logger = logging.getLogger(__name__)

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


class RPOS7CategorySync(object):

    def syncCategories(self):
        context = {}
        errorList = []
        r=requests.get("https://722157.true-order.com/WebReporter/api/v1/categories", headers={"X-Auth-Token":env('POS_AUTH_TOKEN')})
        if(r.status_code==424):
            logger.info("POS is not Reachable in Schedule Category Sync.")
            raise Ignore
        json_data = r.json()
        try:
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
                                    print("Exception in category gofrugle " + str(error))
                                    errorList.append({"Error":str(error)})
                                    pass
                            else:
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
                                    print("Exception in category gofrugle " + str(error))
                                    errorList.append({"Error":str(error)})
                                    pass

                                if catObject.extPosParentId == 0:
                                    pass
                                else:
                                    posObject       = Category.objects.get(extPosId=catObject.extPosParentId)
                                    Category.objects.filter(id=catObject.pk).update(parentId=posObject.pk)

        except Exception as e:
            print("Exception in SyncCategory - RPOS7: " + str(e))
            errorList.append({"Error":str(error)})
            pass
        if errorList:
            errorResponse = ', '.join(d['Error'] for d in errorList)
            logger.error("Exception in Category Sync: %s " %(str(errorResponse)))

        return JsonResponse({'errorcode':'success'})