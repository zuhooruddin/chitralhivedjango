from asyncio import constants
from multiprocessing import context
import re,math

import site
from datetime import datetime, timedelta
from urllib import response
from django.db.models import Sum,Case,When
from django.db.models import Count

from sre_constants import CATEGORY
# from tkinter import N
from unicodedata import category
from unittest import result
from django.shortcuts import render
from inara.models import *
from allauth.socialaccount.models import SocialApp

from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from django.forms.models import model_to_dict
from functools import wraps
from django.http import JsonResponse
import requests
from inara.serializers import *
from inara.core.middlewares.externalPOS.Gofrugal_RPOS7.category import RPOS7Category,RPOS7CategorySync
import json
import environ, boto3
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from django.db.models import OuterRef, Subquery
from rest_framework.decorators import api_view , permission_classes
from rest_framework.pagination import PageNumberPagination
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny,IsAuthenticated
import datetime
from datetime import datetime as currentDateTime
import time,pytz
import importlib
from rest_framework import generics, filters
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import viewsets
from rest_framework.views import APIView
from inara.core import error_codes
from decimal import Decimal
import traceback
from django.db.models import F, Case, When, Value, IntegerField
import logging
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from rest_framework.generics import GenericAPIView
from rest_framework import status
# from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework.decorators import api_view
from rest_framework.response import Response
from allauth.account.forms import default_token_generator
from allauth.account.utils import url_str_to_user_pk as uid_decoder
from allauth.account.utils import user_pk_to_url_str
# from idrisBackend.celery import debug_task
from ecommerce_backend.tasks import sync_categories_click,get_task_status,sync_items_click
from ecommerce_backend.settings import EMAIL_HOST_USER as EMAIL_HOST_USER
from ecommerce_backend.settings import  DEFAULT_SITEMAP_LOCAL as DEFAULT_SITEMAP_LOCAL
from ecommerce_backend.settings import DEFAULT_SITEMAP_S3 as DEFAULT_SITEMAP_S3
from ecommerce_backend.settings import HostDomain as HostDomain
from ecommerce_backend.settings import ImageUrl as ImageUrl

from ecommerce_backend.settings import IMAGE_PROCESSING_RECIPIENTS as IMAGE_PROCESSING_RECIPIENTS

from django.contrib.postgres.search import SearchQuery, SearchVector, TrigramSimilarity
from django.db.models import Q
from rest_framework_simplejwt.views import TokenRefreshView
from .authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
import decimal

from decimal import Decimal
import xml.etree.cElementTree as ET
from django.db.models import F, CharField, Value
from django.db.models.functions import Concat

# debug_task.delay('Hello')
logger = logging.getLogger(__name__)
env = environ.Env()
environ.Env.read_env()
category_POS_type = Category.INTERNAL
product_POS_type= Category.INTERNAL
category_image_type =Category.INTERNAL
product_image_type= Category.INTERNAL
order_POS_type=Category.INTERNAL


from django.contrib.auth.decorators import user_passes_test

# def is_super_admin(user):
#     return user.is_authenticated and user.role == 'super admin'

# def super_admin_required(view_func):
#     return user_passes_test(is_super_admin)(view_func)

from rest_framework.permissions import BasePermission

class IsSuperAdmin(BasePermission):
    # Allows access only to super admin users.
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 1

def is_admin(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if request.user.id is None:
            status = {'ErrorCode': error_codes.ERROR, 'ErrorMsg': error_codes.LOGIN_REQ_MSG}
            logger.info("%s " %(str(status)))
       
            return JsonResponse(status)
        else:
            user = None
            try:
                user = User.objects.get(id=request.user.id, status=User.ACTIVE, role__in=[User.SUPER_ADMIN,User.ADMIN])
            except User.DoesNotExist:
                pass

            if user:
                return view(request, *args, **kwargs)
            else:
                status = {'ErrorCode': error_codes.ERROR, 'ErrorMsg': error_codes.RSTRCTD_CALL_MSG}
                logger.info("%s " %('userID = '+str(request.user.id)+' reponse : '+str(status)))
                return JsonResponse(status)          
    return wrapper

module_name = 'inara.core.middlewares.externalPOS.Gofrugal_RPOS7.category'
class_name = 'RPOS7CategorySync'

item_module_name = 'inara.core.middlewares.externalPOS.Gofrugal_RPOS7.item'
item_class_name = 'RPOS7ItemSync'

customer_module_name = 'inara.core.middlewares.externalPOS.Gofrugal_RPOS7.ecustomer'
customer_class_name = 'RPOS7CustomersSync'

class GoogleLoginView(SocialLoginView):
    authentication_classes = [] # disable authentication, make sure to override `allowed origins` in settings.py in production!
    adapter_class = GoogleOAuth2Adapter
    # callback_url = "https://idrisbookbank-dev.inara.tech"  # frontend application url
    # client_class = OAuth2Client


###### Pagination Setup #######
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 12
class BundleResultsSetPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 25

class AdminResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 20

class CustomResultsSetPagination(PageNumberPagination):
    # page_size = 20
    # page_size_query_param = 'page_size'
    page_size_query_param = 'page_size'
    # max_page_size = 20

class DropdownResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 100

###### Pagination Setup End ########
def class_for_name(module_name, class_name):
    # load the module, will raise ImportError if module cannot be loaded
    objModule = importlib.import_module(module_name)
    # get the class, will raise AttributeError if class cannot be found
    objClassName = getattr(objModule, class_name)
    return objClassName
# class_for_name(module_name, class_name)

############ Sync From FrontEnd #########

# Black List Access Tokken 
# class CustomTokenRefreshView(TokenRefreshView):
#     authentication_classes = [JWTAuthentication]
class BlacklistRefreshView(APIView):
    def post(self, request):
        token = RefreshToken(request.data.get('refresh'))
        token.blacklist()
        accessToken = RefreshToken(request.data.get('accessToken'))
        TokenBlacklist.objects.create(token=accessToken, blacklisted_at=currentDateTime.now())
        return Response("Success")



@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
# @is_admin
@csrf_exempt
def apiSignOut(request):
        context = {}
        # accessToken = request.data
        accessToken = request.data['accessToken']
        user = request.data['userId']
        try:
            outstandingTokenObject = OutstandingToken.objects.filter(user_id=user).values('id')
            for value in outstandingTokenObject:
                token = OutstandingToken.objects.get(id=value['id'])
                if(BlacklistedToken.objects.filter(token=token).exists()):
                    pass
                else:
                    BlacklistedToken.objects.create(token=token)
            logger.info("%s " %(str(request.data)))
            TokenBlacklist.objects.create(token=accessToken, blacklisted_at=currentDateTime.now())
            result = {"ErrorCode": error_codes.SUCCESS, "ErrorMsg": error_codes.ACCESS_TOKEN_BLACKLIST_MSG}
            context.update(result)
            # logger.info("%s " %(str(result)))
        except Exception as e:
            result = {"ErrorCode": error_codes.ERROR, "ErrorMsg": error_codes.ACCESS_TOKEN_NOT_BLACKLIST_MSG}
            context.update(result)
            logger.error("Exception in blackListAccessTokken: %s " %(str(e)))
        return JsonResponse(context, safe=False)

##### END BlackList View #############

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
@is_admin
@csrf_exempt
def adminSyncCategories(request):

    context = {}
    try:
        if(TaskProgress.objects.filter(syncType="CATEGORY_SYNC",status="PROGRESS").exists()):
            result = {'ErrorCode': error_codes.CELERY_ALRDY_TASK_IN_PROCESS, 'ErrorMsg': error_codes.CELERY_ALRDY_TASK_IN_PROGRESS_MSG}
            context.update(result) 
        else:
            # userObj = User.objects.get(id=request.user.id)
            taskProgressObj = TaskProgress.objects.create(progress=0,syncType="CATEGORY_SYNC",status="PROGRESS")
            task = sync_categories_click.delay()
            TaskProgress.objects.filter(id=taskProgressObj.id).update(taskId=task)
            returnObj = TaskProgressSerializers(TaskProgress.objects.get(taskId=task)).data
            result = {'ErrorCode': error_codes.CELERY_PROCESSING, 'ErrorMsg': error_codes.CELERY_PROCESSING_CATEGORY_MSG, 'responseData': returnObj}
            context.update(result) 

    except Exception as e:
        print("Exception ",e)
        logger.error("Exception in adminSyncCategories: %s " %(str(e)))
        result = {'ErrorCode': error_codes.ERROR, 'ErrorMsg': error_codes.CELERY_EXCUTN_FAIL_MSG}
        context.update(result)
    return JsonResponse(context, safe=False)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
@is_admin
@csrf_exempt
def adminSyncItems(request):
   
    context = {}
    try:
        if(TaskProgress.objects.filter(syncType="ITEM_SYNC",status="PROGRESS").exists()):
            result = {'ErrorCode': error_codes.CELERY_ALRDY_TASK_IN_PROCESS, 'ErrorMsg': error_codes.CELERY_ALRDY_TASK_IN_PROGRESS_MSG}
            context.update(result) 
        else:
            # userObj = User.objects.get(id=request.user.id)
            taskProgressObj = TaskProgress.objects.create(progress=0,syncType="ITEM_SYNC",status="PROGRESS")
            time.sleep(3)
            task = sync_items_click.delay()
            TaskProgress.objects.filter(id=taskProgressObj.id).update(taskId=task)
            returnObj = TaskProgressSerializers(TaskProgress.objects.get(taskId=task)).data
            result = {'ErrorCode': error_codes.CELERY_PROCESSING, 'ErrorMsg': error_codes.CELERY_PROCESSING_ITEM_MSG, 'responseData': returnObj}
            context.update(result) 

    except Exception as e:
        print("Exception ",e)
        logger.error("Exception in adminSyncCategories: %s " %(str(e)))
        result = {'ErrorCode': error_codes.ERROR, 'ErrorMsg': error_codes.CELERY_EXCUTN_FAIL_MSG}
        context.update(result)
    return JsonResponse(context, safe=False)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
@is_admin
@csrf_exempt
def categoriesTaskProgress(request):
    context = {}
    try:
        if(TaskProgress.objects.filter(syncType="CATEGORY_SYNC",status="PROGRESS").exists()):
            taskObject = TaskProgress.objects.get(syncType="CATEGORY_SYNC",status="PROGRESS")
            progress = get_task_status(taskObject.taskId)
            taskSerialized = list(TaskProgress.objects.filter(syncType="CATEGORY_SYNC").values('id','taskId','progress','total','uploadTime','completionTime','syncType','status').order_by('-uploadTime')[:5])
            result = {'ErrorCode': error_codes.CELERY_PROCESSING, 'ErrorMsg': error_codes.CELERY_PROCESSING_CATEGORY_MSG,"tasks":taskSerialized, 'progress': progress}
            context.update(result)
        else:
            taskSerialized = list(TaskProgress.objects.filter(syncType="CATEGORY_SYNC").values('id','taskId','progress','total','uploadTime','completionTime','syncType','status','statusReason').order_by('-uploadTime')[:5])
            result = {'ErrorCode': error_codes.CELERY_NO_TASK, 'ErrorMsg': error_codes.CELERY_NO_TSK_IN_PROGRESS_CATEGORY_MSG,"tasks":taskSerialized}
            context.update(result)
    except Exception as e:
        print("Exception ",e)
        logger.error("Exception in categoriesTaskProgress: %s " %(str(e)))
        result = {'ErrorCode': error_codes.ERROR, 'ErrorMsg': error_codes.CELERY_TSK_PRGRS_FAIL_MSG}
        context.update(result)
    return JsonResponse(context, safe=False)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
@is_admin
@csrf_exempt
def itemsTaskProgress(request):
    context = {}
    try:
        if(TaskProgress.objects.filter(syncType="ITEM_SYNC",status="PROGRESS").exists()):
            taskObject = TaskProgress.objects.get(syncType="ITEM_SYNC",status="PROGRESS")
            progress = get_task_status(taskObject.taskId)
            taskSerialized = list(TaskProgress.objects.filter(syncType="ITEM_SYNC").values('id','taskId','progress','total','uploadTime','completionTime','syncType','status').order_by('-uploadTime')[:5])
            result = {'ErrorCode': error_codes.CELERY_PROCESSING, 'ErrorMsg': error_codes.CELERY_PROCESSING_ITEM_MSG,"tasks":taskSerialized, 'progress': progress}
            context.update(result)
        else:
            taskSerialized = list(TaskProgress.objects.filter(syncType="ITEM_SYNC").values('id','taskId','progress','total','uploadTime','completionTime','syncType','status','statusReason').order_by('-uploadTime')[:5])
            result = {'ErrorCode': error_codes.CELERY_NO_TASK, 'ErrorMsg': error_codes.CELERY_NO_TSK_IN_PROGRESS_ITEM_MSG,"tasks":taskSerialized}
            context.update(result)
    except Exception as e:
        print("Exception ",e)
        logger.error("Exception in itemTaskProgress: %s " %(str(e)))
        result = {'ErrorCode': error_codes.ERROR, 'ErrorMsg': error_codes.CELERY_TSK_PRGRS_FAIL_MSG}
        context.update(result)
    return JsonResponse(context, safe=False)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
@is_admin
@csrf_exempt
def stopTaskSync(request):
    taskID = request.query_params.get('id')
    context = {}
    try:
        if(TaskProgress.objects.filter(syncType="ITEM_SYNC",status="PROGRESS").exists()):
            TaskProgress.objects.filter(syncType="ITEM_SYNC",status="PROGRESS").update(cancelTask=True,status="CANCELLED",statusReason="Stopped by admin")
            result = {'ErrorCode': error_codes.SUCCESS, 'ErrorMsg': error_codes.CELERY_TASK_STOP_SUCCESS_MSG}
            context.update(result)
        else:
            result = {'ErrorCode': error_codes.CELERY_ALRDY_COMPLETED, 'ErrorMsg': error_codes.CELERY_TASK_ALREADY_COMPLETED_MSG}
            context.update(result)
    except Exception as e:
        print("Exception ",e)
        logger.error("Exception in itemTaskProgress: %s " %(str(e)))
        result = {'ErrorCode': error_codes.ERROR, 'ErrorMsg': error_codes.CELERY_TASK_STOP_FAILED_MSG}
        context.update(result)
    return JsonResponse(context, safe=False)


############ END ##############
 

############ Categories ############

def syncCategories():
    context = {'Key':'success'}
    className = class_for_name(module_name, class_name)
    syncObj = className()
    # extPos = request.pos
    extPos = 'Gofrugal_RPOS7'
    syncObj.syncCategories()
    return JsonResponse(context)

def getProductCategories(request):
    parentList = []
    try:
        parentLevelCategories = Category.objects.filter(appliesOnline=1 , parentId=None).values('id','name','icon')
        for parent in parentLevelCategories:
            childs =[]
            parents = {'label':parent['name'], 'icon':parent['icon'],'value':parent['id'], 'disabled':False}
            childCategory = Category.objects.filter(appliesOnline=1 , parentId=parent['id']).values('id','name','slug','icon')
            if childCategory:
                for child in childCategory:
                    childs.append({'label':child['name'],'value':child['id'], 'children':[],'disabled':False})
                    parents['disabled'] = True
            parents['children'] = childs
            parentList.append(parents)
    except Exception as e:
        logger.error("Exception in getProductCategories: %s " %(str(e)))
    return JsonResponse(parentList, safe=False)


def getNavCategories(request):
    parentList = []
    try:
        parentLevelCategories = Category.objects.filter(parentId=None, isBrand=False, status=Category.ACTIVE).values('id','name','icon','slug')
        for parent in parentLevelCategories:
            childs =[]
            parents = {"title":parent['name'],"slug":parent['slug'], "icon":parent['icon'],"id":parent['id'], "menuComponent":"MegaMenu1","href":"/category/"+parent['slug']}
            childCategory = Category.objects.filter(parentId=parent['id'], status=Category.ACTIVE).values('id','name','slug','icon')
            if childCategory:
                for child in childCategory:
                    subChilds =[]
                    subCategory = Category.objects.filter(parentId=child['id'], status=Category.ACTIVE).values('id','name','slug','icon')
                    if subCategory:
                        for sub in subCategory:
                            subChilds.append({'title':sub['name'],"href":"/category/"+sub['slug']})
                    childs.append({"title":child['name'],"slug":parent['slug'],"href":"/category/"+child['slug'],"subCategories":subChilds})
                    
            parents['menuData'] = {"categories":childs}
            parentList.append(parents)
    except Exception as e:
        logger.error("Exception in getNavCategories: %s " %(str(e)))
    return JsonResponse(parentList, safe=False)








def showAllNavCategories(request):
    slug = request.GET.get('slug')
    parentList = []
    try:
        parentLevelCategories = Category.objects.filter(parentId=None, isBrand=False, slug=slug, status=Category.ACTIVE).values('id','name','icon','slug')
        for parent in parentLevelCategories:
            childs =[]
            parents = {"title":parent['name'],"slug":parent['slug'], "icon":parent['icon'],"id":parent['id'], "menuComponent":"MegaMenu1","href":"/category/"+parent['slug']}
            childCategory = Category.objects.filter(parentId=parent['id'], status=Category.ACTIVE).values('id','name','slug','icon')
            if childCategory:
                for child in childCategory:
                    subChilds =[]
                    subCategory = Category.objects.filter(parentId=child['id'], status=Category.ACTIVE).values('id','name','slug','icon')
                    if subCategory:
                        for sub in subCategory:
                            subChilds.append({'title':sub['name'],"href":"/category/"+sub['slug']})
                    childs.append({"title":child['name'],"icon":child['icon'],"slug":parent['slug'],"href":"/category/"+child['slug'],"subCategories":subChilds})
                    
            parents['menuData'] = {"categories":childs}
            parentList.append(parents)
        if not parentLevelCategories:
            # no exact matches found
            search = slug.replace("-"," ")
            searchWords = search.split(" ")
            firstWord = ''
            thirdWord = ''
            secondWord = ''
            if len(searchWords)>=1:
                firstWord = searchWords[0]
                query = SearchQuery(search) | SearchQuery(firstWord) 
            if len(searchWords)>=2:
                secondWord = searchWords[1]
                query = SearchQuery(search) | SearchQuery(firstWord) | SearchQuery(secondWord)  
            if len(searchWords)>=3:
                thirdWord = searchWords[2]
                query = SearchQuery(search) | SearchQuery(firstWord) | SearchQuery(secondWord) | SearchQuery(thirdWord) 

            search_vector = SearchVector("name")
            # search_query = SearchQuery("books nts") | SearchQuery("nts") | SearchQuery("books")  #SearchQuery(searchWords)
            categories = Category.objects.annotate(
                     rank=SearchRank(search_vector, query)
                ).filter(isBrand=False,status=Category.ACTIVE,rank__gt=0).order_by("-rank")
            childs = []
            parents=[]
            parents = {"title":slug,"slug":slug}
            for cat in categories:
                childs.append({"title":cat.name,"icon":cat.icon.name,"slug":cat.slug,"href":"/category/"+cat.slug})
            parents['menuData'] = {"categories":childs}
            parentList.append(parents)
    except Exception as e:
        print(e)
        logger.error("Exception in getNavCategories: %s " %(str(e)))
    return JsonResponse(parentList, safe=False)
def getmyCategories(request):
    menuCategory = {}
    returnList = []
    
    try:
        parentLevelCategories = Category.objects.filter(appliesOnline=1 , parentId=None).values('id','name','icon')
        for parent in parentLevelCategories:
            parents = {'name':parent['name'], 'icon':parent['icon'],'id':parent['id']}
            childCategory = Category.objects.filter(appliesOnline=1 , parentId=parent['id']).values('id','name','slug','icon')
            parents['menuData']= {'categories':list(childCategory)}
            returnList.append(parents)
    except Exception as e:
        logger.error("Exception in getmyCategories: %s " %(str(e)))

    return JsonResponse(returnList, safe=False)
#################GET EXTERNAL +INTERNAL#########################
def getAllCategories(request):
    sortedList = []
    try:
        categoryObject = list(Category.objects.filter(isBrand=False,parentId=None).values('id','slug','extPosId','parentId','name','description','showAtHome','icon'))
        for cat in categoryObject:
            sortedList = sortedList + [cat]
            children = list(Category.objects.filter(isBrand=False,parentId=cat['id']).values('id','slug','extPosId','parentId','parentId__name','name','description','showAtHome','icon'))
            sortedList = sortedList+children
    except Exception as e:
        logger.error("Exception in getAllCategories: %s " %(str(e)))
    return JsonResponse(sortedList, safe=False)



#######################getAllPaginatedCategories Local + External#################

# @method_decorator(api_view(["GET", "POST"]), name='dispatch')
@permission_classes((IsAuthenticated,))
# @method_decorator(is_admin, name='dispatch')
class getAllPaginatedCategories(generics.ListCreateAPIView):
    serializer_class = CategorySerializerDepth
    pagination_class = CustomResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'extPosId']

    def get_queryset(self):
        categoryObject = Category.objects.filter(isBrand=False,status=1)
        return categoryObject
    





def getParentCategories(request):
    categoryObject = {}
    try:
        categoryObject = list(Category.objects.filter(appliesOnline=1,parentId__isnull=True).values('id','extPosId','parentId','name').order_by('name'))
    except Exception as e:
        logger.error("Exception in getParentCategories: %s " %(str(e)))
    return JsonResponse(categoryObject, safe=False)






def getSubCategories(request):
    categoryObject = {}
    try:
        categoryObject = list(Category.objects.filter(appliesOnline=1,parentId__isnull=False).values('id','extPosId','parentId','name').order_by('name'))
    except Exception as e:
        logger.error("Exception in getSubCategories: %s " %(str(e)))
    return JsonResponse(categoryObject, safe=False)

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
@is_admin
@csrf_exempt
def getCategory(request):
    categoryObject = {}
    slug = request.data['slug']
    category_POS_type=request.data['pos']
    
    

    try:
        if category_POS_type ==1:
            categoryObject = list(Category.objects.filter(slug=slug, posType =Category.INTERNAL).values('id','extPosId','slug','parentId','name','description','showAtHome','icon','metaUrl','metaTitle','metaDescription','status').order_by('parentId'))
    
        elif category_POS_type ==2:
            categoryObject = list(Category.objects.filter(slug=slug,posType=Category.EXTERNAL ).values('id','extPosId','slug','parentId','name','description','showAtHome','icon','metaUrl','metaTitle','metaDescription','status').order_by('extPosId','parentId'))
        else:
            categoryObject = list(Category.objects.filter(slug=slug,posType=Category.MIX ).values('id','extPosId','slug','parentId','name','description','showAtHome','icon','metaUrl','metaTitle','metaDescription','status').order_by('extPosId','parentId'))


            
    except Exception as e:
        logger.error("Exception in getCategory: %s " %(str(e)))
    return JsonResponse(categoryObject, safe=False)






# @method_decorator(api_view(["GET", "POST"]), name='dispatch')
@permission_classes((IsAuthenticated,))
# @method_decorator(is_admin, name='dispatch')
class getAllBrand(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    pagination_class = AdminResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name','slug']

    def get_queryset(self):
        brandObject={}
        try:
            brandObject = Category.objects.filter(isBrand=True)
        except Exception as e:
            logger.error("Exception in getAllBrand: %s " %(str(e)))
        return brandObject

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
@is_admin
@csrf_exempt
def getBrand(request):
    brandObject = {}
    slug = request.data['slug']
    try:
        brandObject = list(Category.objects.filter(slug=slug).values('id','slug','extPosId','parentId','name','description','showAtHome','icon','metaUrl','metaTitle','metaDescription'))
    except Exception as e:
        logger.error("Exception in getBrand: %s " %(str(e)))
    return JsonResponse(brandObject, safe=False)


# @api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
# @csrf_exempt
class getSearchCategory(generics.ListCreateAPIView):
    serializer_class = ItemSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        itemObject={}
        slug = self.request.query_params['slug']
        try:
            categoryObject = Category.objects.get(slug=slug)
            itemList = []
            categoryItemObject = CategoryItem.objects.filter(categoryId=categoryObject.pk).values("itemId").distinct("itemId")
            for i in categoryItemObject:
                itemList.append(i['itemId'])
            itemObject = Item.objects.filter(id__in=itemList,status=Item.ACTIVE,appliesOnline=1).order_by("-newArrivalTill","-isFeatured","-stock")
        except Exception as e:
            logger.error("Exception in getSearchCategory: %s " %(str(e)))
        return itemObject

@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def getCategoryDetail(request):
    categorySerialized = {}
    slug = request.data['slug']
    try:
        categoryObject = Category.objects.get(slug=slug)
        categorySerialized = CategorySerializer(categoryObject).data
    except Exception as e:
        logger.error("Exception in getCategoryDetail: %s " %(str(e)))
    return JsonResponse(categorySerialized, safe=False)

############## Paginations ####################
# @api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
# @csrf_exempt
class PaginatedCategory(generics.ListCreateAPIView):
    serializer_class = ItemSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        itemObject={}
        slug = self.request.query_params['slug']
        try:
            categoryObject = Category.objects.get(slug=slug)
            itemList = []
            categoryItemObject = CategoryItem.objects.filter(categoryId=categoryObject.pk).values("itemId").distinct("itemId")
            for i in categoryItemObject:
                itemList.append(i['itemId'])
            itemObject = Item.objects.filter(id__in=itemList,status=Item.ACTIVE,appliesOnline=1).order_by("-newArrivalTill","-isFeatured","-stock")
        except Exception as e:
            logger.error("Exception in PaginatedCategory: %s " %(str(e)))
        return itemObject
    
@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def get_all_paginated_items(request):
    slug = request.GET.get('slug', '')
    page = request.GET.get('page', 1)
    page_size = request.GET.get('pageSize', 9)
    sort_option = request.GET.get('sort', '')  # Get the sort option

    try:
        # categoryObject = Category.objects.get(slug=slug)
        categoryObject = Category.objects.get(slug=slug)

    


        itemList = []
        categoryItemObject = CategoryItem.objects.filter(categoryId=categoryObject.pk, status=CategoryItem.ACTIVE).values("itemId").distinct("itemId")
        

        for i in categoryItemObject:
            itemList.append(i['itemId'])

        # itemObject = Item.objects.filter(id__in=itemList, status=Item.ACTIVE, appliesOnline=1)
        itemObject = Item.objects.filter(id__in=itemList, status=Item.ACTIVE)

        
        
        itemObject = itemObject.order_by("-newArrivalTill", "-isFeatured", "-stock")
        if sort_option == 'price_asc':
            itemObject = itemObject.order_by("salePrice")  
        elif sort_option == 'price_desc':
            itemObject = itemObject.order_by("-salePrice") 

        paginator = Paginator(itemObject, page_size)
        page_obj = paginator.get_page(page)

        serializer = ItemSerializer(page_obj, many=True)
        data = {
            'results': serializer.data,
            'count': paginator.count
        }
    except Exception as e:
        print(e)
        logger.error("Exception in get_all_paginated_items: %s " % (str(e)))

    return Response(data)





#########################EXTERNAL ADD CATEGORY#####################################################
# @method_decorator(api_view(["POST"]), name='dispatch')
@permission_classes((IsAuthenticated,))
# @method_decorator(is_admin, name='dispatch')
class addCategory(generics.CreateAPIView):
        result = {}
        queryset = Category.objects.all()
        serializer_class = CategorySerializer
        parser_classes = (MultiPartParser, FormParser)
        # permission_classes = [IsAuthenticated,]

# @method_decorator(api_view(["PUT", "PATCH"]), name='dispatch')
# @permission_classes((IsAuthenticated,))
# @method_decorator(is_admin, name='dispatch')
class updateCategory(generics.UpdateAPIView):
        result = {}
        queryset = Category.objects.all()
        serializer_class = CategorySerializer
        parser_classes = (MultiPartParser, FormParser)
        permission_classes = [IsAuthenticated,]

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
@is_admin
@csrf_exempt
def deleteCategory(request):
        context = {}
        categoryID = request.data
        logger.info("Request: %s" %(request.data))
        try:
            if(Category.objects.filter(id=categoryID,appliesOnline=1).exists()):
                result = {"ErrorCode": error_codes.ERROR, "ErrorMsg": error_codes.CTGRY_FRM_POS_ERR_MSG}
            else:
                categoryObject = Category.objects.get(id=categoryID)
                if(CategoryItem.objects.filter(categoryId=categoryObject).exists()):
                    result = {"ErrorCode": error_codes.ERROR, "ErrorMsg": error_codes.CTGRY_EXST_IN_ITEM_ERR_MSG}
                else:
                    if(Individual_BoxOrder.objects.filter(category_id=categoryObject).exists()):
                        result = {"ErrorCode": error_codes.ERROR, "ErrorMsg": error_codes.CTGRY_EXST_IN_BX_ORDR_ERR_MSG}
                    else:
                        Category.objects.filter(id = categoryID).delete()
                        result = {"ErrorCode": error_codes.SUCCESS, "ErrorMsg": error_codes.DELETE_MSG}
            context.update(result)
            # logger.info("%s " %(str(result)))
        except Exception as e:
            result = {"ErrorCode": error_codes.ERROR, "ErrorMsg": error_codes.NOT_DELETE_MSG}
            context.update(result)
            print("Exception in Delete Bundle View ", str(e))
            logger.error("Exception in deleteCategory: %s " %(str(e)))
            # traceback.print_exc()
        return JsonResponse(context, safe=False)

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
@is_admin
@csrf_exempt
def checkCategoryChange(request):
    result = {}
    data = request.data
    imagePath = data['icon'].rsplit('media/', 1)[1]
    logger.info("Request: %s" %(request.data))
    try:
        if(Individual_BoxOrder.objects.filter(category_id=data['id']).exists()):
            # print('IndividualBoxOrder id Exists')
            individualBoxOrderObject = Individual_BoxOrder.objects.filter(category_id=data['id']).update(category_slug=data['slug'],category_name=data['name'],image=imagePath,parent=data['parentId'])
            # print('########## individualBoxOrderObject #########')
            # print(individualBoxOrderObject)
        # if(SectionSequence.objects.filter(category_id=data['id']).exists):
        #     SectionSequence.objects.filter(category_id=data['id']).update(category_slug = data['slug'], name = data['name'])
        # if(SectionSequence.objects.filter(child1_id=data['id']).exists):
        #     SectionSequence.objects.filter(child1_id=data['id']).update(child1_slug = data['slug'], child1_name = data['name'])
        # if(SectionSequence.objects.filter(child2_id=data['id']).exists):
        #     SectionSequence.objects.filter(child2_id=data['id']).update(child2_slug = data['slug'], child2_name = data['name'])
        # if(SectionSequence.objects.filter(child3_id=data['id']).exists):
        #     SectionSequence.objects.filter(child3_id=data['id']).update(child3_slug = data['slug'], child3_name = data['name'])
        # if(SectionSequence.objects.filter(child4_id=data['id']).exists):
        #     SectionSequence.objects.filter(child4_id=data['id']).update(child4_slug = data['slug'], child4_name = data['name'])
        # if(SectionSequence.objects.filter(child5_id=data['id']).exists):
        #     SectionSequence.objects.filter(child5_id=data['id']).update(child5_slug = data['slug'], child5_name = data['name'])
        # if(SectionSequence.objects.filter(child6_id=data['id']).exists):
        #     SectionSequence.objects.filter(child6_id=data['id']).update(child6_slug = data['slug'], child6_name = data['name'])
        # if(SectionSequence.objects.filter(child7_id=data['id']).exists):
        #     SectionSequence.objects.filter(child7_id=data['id']).update(child7_slug = data['slug'], child7_name = data['name'])
        # if(SectionSequence.objects.filter(child8_id=data['id']).exists):
        #     SectionSequence.objects.filter(child8_id=data['id']).update(child8_slug = data['slug'], child8_name = data['name'])
        
        result = {"ErrorCode": error_codes.SUCCESS, "ErrorMsg": error_codes.SUCCESS_MSG}
    except Exception as e:
        logger.error("Exception in checkCategoryChange: %s " %(str(e)))
        result = {"ErrorCode": error_codes.ERROR, "ErrorMsg": error_codes.ERROR_MSG}
        
    return JsonResponse(result, safe=False)

############# Customers #####################
# @method_decorator(api_view(["GET", "POST"]), name='dispatch')
@permission_classes((IsAuthenticated,))
# @method_decorator(is_admin, name='dispatch')
class getAllCustomers(generics.ListCreateAPIView):
    serializer_class = UserSerializer
    pagination_class = AdminResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'username','mobile','address']

    def get_queryset(self):
        try:
            userObject = User.objects.filter(role=3,status=1)
        except Exception as e:
            logger.error("Exception in getAllCustomers: %s " %(str(e)))
        return userObject

############## Items ##########################

def syncItems():
    context = {'Key':'success'}
    className = class_for_name(item_module_name, item_class_name)
    syncObj = className()
    # extPos = request.pos
    extPos = 'Gofrugal_RPOS7'
    syncObj.syncItems()
    return JsonResponse(context)

def getAllItems(request):
    itemObject = {}
    try:
        itemObject = list(Item.objects.filter(appliesOnline=1).values('id','sku','slug','extPosId','name','description','mrp','salePrice','stock','aliasCode','status','manufacturer', 'image').order_by('extPosId')[:100])
    except Exception as e:
            logger.error("Exception in getAllItems: %s " %(str(e)))
    return JsonResponse(itemObject, safe=False)

# @method_decorator(api_view(["GET", "POST"]), name='dispatch')
@permission_classes((IsAuthenticated,))
# @method_decorator(is_admin, name='dispatch')
class getAllPaginatedItems(generics.ListCreateAPIView):
    serializer_class = ItemSerializer
    pagination_class = CustomResultsSetPagination
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    # filterset_fields = {'author': ['startswith'],'manufacturer': ['startswith']}
    filterset_fields = ['author','manufacturer']

    search_fields = ['name', 'sku','isbn']

    def get_queryset(self):
        itemObject={}
        try:
            itemObject = Item.objects.filter()
        except Exception as e:
            logger.error("Exception in getAllPaginatedItems: %s " %(str(e)))
        return itemObject

# @method_decorator(api_view(["GET", "POST"]), name='dispatch')
@permission_classes((IsAuthenticated,))
# @method_decorator(is_admin, name='dispatch')
class getAllPaginatedItemsForBundle(generics.ListCreateAPIView):
    serializer_class = ItemSerializer
    pagination_class = DropdownResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'sku']

    def get_queryset(self):
        itemObject={}
        try:
            itemObject = Item.objects.filter(status=1)
        except Exception as e:
            logger.error("Exception in getAllPaginatedItemsForBundle: %s " %(str(e)))
        return itemObject
    


##############################Internal

@permission_classes((IsAuthenticated,))
# @method_decorator(is_admin, name='dispatch')
class getAllInternalPaginatedItemsForBundle(generics.ListCreateAPIView):
    serializer_class = ItemSerializer
    pagination_class = DropdownResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'sku']

    def get_queryset(self):
        itemObject={}
        try:
            itemObject = Item.objects.filter(status=1)
        except Exception as e:
            logger.error("Exception in getAllPaginatedItemsForBundle: %s " %(str(e)))
        return itemObject

#################

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
@is_admin
@csrf_exempt
def getItem(request):
    itemObject = {}
    id = request.data['id']
    try:
        itemObject = list(Item.objects.filter(id=int(id)).values('id','extPosId','slug','extPosId','sku','name','description','mrp','salePrice','stock','aliasCode','status','author','manufacturer', 'image', 'length', 'height', 'width','isNewArrival','newArrivalTill','metaUrl','metaTitle','metaDescription','itemInstructions','youtube_link','facebook_link','twitter_link','instagram_link','stock','stockCheckQty','isFeatured').order_by('extPosId'))
    except Exception as e:
            logger.error("Exception in getItem: %s " %(str(e)))
    return JsonResponse(itemObject, safe=False)

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
@is_admin
@csrf_exempt
def getItemCategory(request):
    itemObject = {}
    itemId = request.data['id']
    try:
        itemObject = list(CategoryItem.objects.filter(itemId=itemId).values('id','level','status','categoryId','itemId'))
    except Exception as e:
            logger.error("Exception in getItemCategory: %s " %(str(e)))
    return JsonResponse(itemObject, safe=False)

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
@is_admin
@csrf_exempt
def getItemGallery(request):
    itemGalleryObject = {}
    id = request.data['id']
    try:
        itemObject = Item.objects.get(id = id)
        itemGalleryObject = list(ItemGallery.objects.filter(itemId=itemObject).values('id','image','status','itemId'))
    except Exception as e:
            logger.error("Exception in getItemGallery: %s " %(str(e)))
    return JsonResponse(itemGalleryObject, safe=False)

@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def getSearchItem(request):
    context = {}
    returnList=[]
    slug = request.data['id']
    try:
        itemObject = Item.objects.get(slug=slug)
        parentList = {'price': itemObject.mrp, 'title':itemObject.name,'imgUrl':itemObject.image.url,'category':'Category','manufacturer':itemObject.manufacturer,'aliasCode':itemObject.aliasCode,'description':itemObject.description,'instructions':itemObject.itemInstructions,'discount':0,'rating':3,'imgGroup':[]}
        galleryObject = ItemGallery.objects.filter(itemId=itemObject.pk).values('id','image','status','itemId')
        for image in galleryObject:
            parentList['imgGroup'].append(image['image'])
        returnList.append(parentList)
    except Exception as e:
            logger.error("Exception in getSearchItem: %s " %(str(e)))
    return JsonResponse(returnList, safe=False)


@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def getItemDetail(request):
    returnList=[]
    slug = request.data['slug']
    publisherFlag = False
    try:
        itemObject = Item.objects.get(slug=slug)
        categoryList = list(CategoryItem.objects.filter(itemId=itemObject,status=CategoryItem.ACTIVE).values_list("categoryId",flat=True))
       
        categoriesObj = Category.objects.filter(id__in=categoryList)

      
        # publisherCat = PublisherFlag()
        # for categoryObject in categoriesObj:
        #     if categoryObject.slug in publisherCat:
        #         publisherFlag = True
        #         break
        #     else:
        #         for parentCat in publisherCat:
        #             parentPId = Category.objects.get(slug=parentCat)
        #             if categoryObject.parentId == parentPId:
        #                 publisherFlag = True
        #                 break
        parentList = {'id':itemObject.id ,'slug':itemObject.slug,'isbn': itemObject.isbn,'length':itemObject.length,'width':itemObject.width,'height':itemObject.height,'weight':itemObject.weight,'mrp': itemObject.mrp,'salePrice':itemObject.salePrice,'sku':itemObject.sku,'stock':itemObject.stock,'name':itemObject.name,'imgUrl':itemObject.image.name,'category':'Category','manufacturer':itemObject.manufacturer,'author':itemObject.author,'aliasCode':itemObject.aliasCode,'description':itemObject.description,'instructions':itemObject.itemInstructions,'metaTitle':itemObject.metaTitle,'metaDescription':itemObject.metaDescription,'metaUrl':itemObject.metaUrl,'isNewArrival':itemObject.isNewArrival,'discount':itemObject.discount,'rating':3,'imgGroup':[],'publisherFlag':publisherFlag}
        galleryObject = ItemGallery.objects.filter(itemId=itemObject.pk).values('id','image','status','itemId')
        parentList['imgGroup'].append(itemObject.image.name,)
        
        for image in galleryObject:
            parentList['imgGroup'].append(image['image'])
        returnList.append(parentList)
    except Exception as e:
            print(e)
            logger.error("Exception in getSearchItem: %s " %(str(e)))
    return JsonResponse(returnList, safe=False)


# @method_decorator(api_view(["PUT", "PATCH"]), name='dispatch')
@permission_classes((IsAuthenticated,))
# @method_decorator(is_admin, name='dispatch')
class updateItem(generics.UpdateAPIView):
        result = {}
        queryset = Item.objects.all()
        serializer_class = ItemSerializer
        parser_classes = (MultiPartParser, FormParser)
        permission_classes = [IsAuthenticated,]

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
@is_admin
@csrf_exempt
def updateItemGallery(request,pk):
    context = {}
    returnList=[]
    listImages = request.FILES.getlist('image')
    try:
        itemObject = Item.objects.get(id=pk)
        for i in listImages:
            galleryObj = ItemGallery.objects.create(image=i,itemId=itemObject)
    except Exception as e:
            logger.error("Exception in updateItemGallery: %s " %(str(e)))

    return JsonResponse(returnList, safe=False)

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
@is_admin
@csrf_exempt
def updateItemCategory(request,pk):
    context = {}
    listCategory = request.data
    logger.info("Request: %s" %(request.data))
    try:
        oldCategoryList = list(CategoryItem.objects.filter(itemId = pk).values('categoryId'))
        oldCategoryList = [f['categoryId'] for f in oldCategoryList]
        for newListValue in listCategory:
            creationFlag = True
            for oldListValue in oldCategoryList:
                if newListValue['id'] == oldListValue:
                    creationFlag = False
                    oldCategoryList.remove(oldListValue)
            if(creationFlag):
                categoryObject = Category.objects.get(id=newListValue['id'])
                itemObject     = Item.objects.get(id=pk)
                CategoryItem.objects.create(categoryId=categoryObject,itemId=itemObject)
                    
        if(oldCategoryList):
            for value in oldCategoryList:
                categoryItemObject = CategoryItem.objects.get(itemId=pk,categoryId=value)
                categoryItemObject.delete()
        result = {"ErrorCode": error_codes.SUCCESS, "ErrorMsg": error_codes.CTGRY_ITEM_UPDATE_SUCCESS_MSG}
        context.update(result)
    except Exception as e:
        result = {"ErrorCode": error_codes.ERROR, "ErrorMsg": error_codes.CTGRY_ITEM_NOT_UPDATE_ERR_MSG}
        context.update(result)
        print("Exception in Update Item Category ", str(e))
        logger.error("Exception in updateItemCategory: %s " %(str(e)))

    return JsonResponse(context, safe=False)
        

############### Bundles ###################

# def getAllBrandBundle(request):
#     context = {}
#     itemObject = list(Bundle.objects.filter(status=Bundle.ACTIVE,bundleType=Bundle.BRAND).values('id','name','slug','sku','bundleType','image','price','salePrice','description','showAtHome','metaUrl','metaTitle','metaDescription','status'))
#     return JsonResponse(itemObject, safe=False)

# @method_decorator(api_view(["GET", "POST"]), name='dispatch')
@permission_classes((IsAuthenticated,))
# @method_decorator(is_admin, name='dispatch')
class getAllBrandBundle(generics.ListCreateAPIView):
    serializer_class = BundleSerializer
    pagination_class = AdminResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'sku']

    def get_queryset(self):
        itemObject={}
        try:
            itemObject = Bundle.objects.filter(status=Bundle.ACTIVE,bundleType=Bundle.BRAND)
        except Exception as e:
            print("Exception in getAllBRANDBundle", str(e))
        return itemObject

# @method_decorator(api_view(["GET", "POST"]), name='dispatch')
@permission_classes((IsAuthenticated,))
# @method_decorator(is_admin, name='dispatch')
class getAllProductBundle(generics.ListCreateAPIView):
    serializer_class = BundleSerializer
    pagination_class = AdminResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'sku']

    def get_queryset(self):
        itemObject={}
        try:
            itemObject = Bundle.objects.filter(status=Bundle.ACTIVE,bundleType=Bundle.PRODUCT)
        except Exception as e:
            print("Exception in getAllProductBundle", str(e))
        return itemObject

# def getAllProductBundle(request):
#     context = {}
#     itemObject = list(Bundle.objects.filter(status=Bundle.ACTIVE,bundleType=Bundle.PRODUCT).values('id','name','slug','sku','image','mrp','salePrice','description','showAtHome','metaUrl','metaTitle','metaDescription'))
#     return JsonResponse(itemObject, safe=False)

# @method_decorator(api_view(["POST"]), name='dispatch')
@permission_classes((IsAuthenticated,))
# @method_decorator(is_admin, name='dispatch')
class addBundle(generics.CreateAPIView):
        result = {}
        queryset = Bundle.objects.all()
        serializer_class = BundleSerializer
        parser_classes = (MultiPartParser, FormParser)
        permission_classes = [IsAuthenticated,]

# @method_decorator(api_view(["PUT", "PATCH"]), name='dispatch')
@permission_classes((IsAuthenticated,))
# @method_decorator(is_admin, name='dispatch')
class updateBundle(generics.UpdateAPIView):
        result = {}
        queryset = Bundle.objects.all()
        serializer_class = BundleSerializer
        parser_classes = (MultiPartParser, FormParser)
        permission_classes = [IsAuthenticated,]

# @api_view(['GET', 'POST'])
# @permission_classes((AllowAny,))
# @csrf_exempt
# def getItem(request):
#     context = {}
#     # print(request.data['id'])
#     id = request.data['id']
#     # print("id backend getCategory")
#     # print(id)
#     categoryObject = list(Item.objects.filter(appliesOnline=1,id=int(id)).values('id','slug','extPosId','sku','name','description','mrp','salePrice','stock','aliasCode','status','manufacturer', 'image', 'length', 'height', 'width','isNewArrival','newArrivalTill','metaUrl','metaTitle','metaDescription','itemInstructions','youtube_link','facebook_link','twitter_link','instagram_link','stock','stockCheckQty').order_by('extPosId'))
#     # context = {"categories": categoryObject}
#     return JsonResponse(categoryObject, safe=False)

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
@is_admin
@csrf_exempt
def deleteBundle(request):
        context = {}
        bundleId = request.data
        logger.info("Request: %s" %(request.data))
        try:
            # userObject = User.objects.filter(id=valueDict['id']).update(name=valueDict['name'],email=valueDict['email'],mobile=valueDict['mobile'],status=valueDict['status'])
            bundleItemObject = BundleItem.objects.filter(bundleId = bundleId).delete()
            bundleObject = Bundle.objects.filter(id=bundleId).delete()
            # print(bundleItemObject)
            # print(bundleObject)
            result = {"ErrorCode": error_codes.SUCCESS, "ErrorMsg": error_codes.DELETE_MSG, "Bundle":bundleObject}
            context.update(result)
            logger.info("%s " %(str(bundleObject)))
        except Exception as e:
            result = {"ErrorCode": error_codes.ERROR, "ErrorMsg": error_codes.NOT_DELETE_MSG}
            context.update(result)
            print("Exception in Delete Bundle View ", str(e))
            logger.error("Exception in deleteBundle: %s " %(str(e)))
            # traceback.print_exc()
        return JsonResponse(context, safe=False)

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
@is_admin
@csrf_exempt
def updatePriorityBundleItem(request):
        context = {}
        priority = request.data
        # print(priority)
        try:
            for i in priority:
                BundleItem.objects.filter(bundleId_id=i['bundleId'], itemId_id=i['itemId']).update(priority=i['priority'])
            result = {"ErrorCode": error_codes.SUCCESS, "ErrorMsg": error_codes.UPDATE_MSG}
            context.update(result)
        except Exception as e:
            result = {"ErrorCode": error_codes.ERROR, "ErrorMsg": error_codes.NOT_UPDATE_MSG}
            context.update(result)
            print("Exception in updatePriorityBundleItem ", str(e))
        return JsonResponse(context, safe=False)

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
@is_admin
@csrf_exempt
def getBundle(request):
    bundleDetail = {}
    bundleItem = {}
    slug = request.data['slug']
    try:
        bundleObject = Bundle.objects.get(slug=slug)
        bundleDetail = list(Bundle.objects.filter(slug=slug).values('id','name','slug','sku','image','mrp','salePrice','description','metaUrl','metaTitle','metaDescription','status','bundleType', 'categoryId'))
        bundleItem   = list(BundleItem.objects.filter(bundleId=bundleObject).values('id','quantity','status','bundleId','itemId').annotate(name=F('itemId__name'), mrp=F('itemId__mrp'), salePrice=F('itemId__salePrice')))
    except Exception as e:
            logger.error("Exception in getBundle: %s " %(str(e)))
    return JsonResponse({'bundleDetail':bundleDetail,'bundleItem':bundleItem}, safe=False)

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
@is_admin
@csrf_exempt
def getBundleItemsForAdminConfiguration(request):
    bundleDetail = {}
    bundleItem = {}
    id = request.data['id']
    try:
        bundleObject = Bundle.objects.get(id=id)
        # bundleDetail = list(Bundle.objects.filter(slug=slug).values('id','name','slug','sku','image','mrp','salePrice','description','metaUrl','metaTitle','metaDescription','status','bundleType', 'categoryId'))
        bundleItem   = list(BundleItem.objects.filter(bundleId=bundleObject).values('id','quantity','status','bundleId','itemId').annotate(name=F('itemId__name')).order_by('priority'))
    except Exception as e:
            logger.error("Exception in getBundleItemsForAdminConfiguration: %s " %(str(e)))
    return JsonResponse({'tasks':bundleItem}, safe=False)

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
@is_admin
@csrf_exempt
def getBundleForAdminConfiguration(request):
    try:
        bundleObject = list(Bundle.objects.filter(status=Bundle.ACTIVE).values('id','name','slug','bundleType'))
    except Exception as e:
            logger.error("Exception in getBundleForAdminConfiguration: %s " %(str(e)))
    return JsonResponse({'bundles':bundleObject}, safe=False)

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
@is_admin
@csrf_exempt
def updateBundleItemPriority(request):
    bundleDetail = {}
    bundleItem = {}
    try:
        bundleObject = list(Bundle.objects.filter(status=Bundle.ACTIVE).values('id','name','slug','bundleType'))
    except Exception as e:
            logger.error("Exception in updateBundleItemPriority: %s " %(str(e)))
    return JsonResponse({'bundles':bundleObject}, safe=False)

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
@is_admin
@csrf_exempt
def getBundleTypes(request):
    try:
        # bundleObject = list(Bundle.objects.filter(status=Bundle.ACTIVE).values('id','name','slug','bundleType'))
        bundleObject = list(Bundle.objects.order_by().values('bundleType').distinct())
    except Exception as e:
            logger.error("Exception in getBundleTypes: %s " %(str(e)))
    return JsonResponse({'bundleTypes':bundleObject}, safe=False)

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
@is_admin
@csrf_exempt
def getBundleForPrioritySet(request):
    bundleDetail = {}
    bundleItem = {}
    bundleType = request.data['bundleType']
    try:
        # bundleObject = Bundle.objects.get(bundleType=bundleType)
        # bundleDetail = list(Bundle.objects.filter(slug=slug).values('id','name','slug','sku','image','mrp','salePrice','description','metaUrl','metaTitle','metaDescription','status','bundleType', 'categoryId'))
        if(bundleType=="BrandCategory"):
            bundleItem   = list(Category.objects.filter(isBrand=True,status=Category.ACTIVE).values('id','name','slug').order_by('priority'))
        else:
            bundleItem   = list(Bundle.objects.filter(bundleType=bundleType, status=Bundle.ACTIVE).values('id','name','sku','slug','bundleType').order_by('priority'))
    except Exception as e:
            logger.error("Exception in getBundleForPrioritySet: %s " %(str(e)))
    return JsonResponse({'tasks':bundleItem}, safe=False)

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
@is_admin
@csrf_exempt
def updateBundlePriority(request):
        context = {}
        priority = request.data
        # print(priority)
        
        try:
            if(priority['priorityType'] == "BrandCategory"):
                for i in priority['tasks']:
                    Category.objects.filter(id=i['id']).update(priority=i['priority'])
            else:
                for i in priority['tasks']:
                    Bundle.objects.filter(id=i['id']).update(priority=i['priority'])
            result = {"ErrorCode": error_codes.SUCCESS, "ErrorMsg": error_codes.UPDATE_MSG}
            context.update(result)
        except Exception as e:
            result = {"ErrorCode": error_codes.ERROR, "ErrorMsg": error_codes.NOT_UPDATE_MSG}
            context.update(result)
            print("Exception in updateBundlePriority ", str(e))
        return JsonResponse(context, safe=False)

# @api_view(['GET', 'POST'])
# @permission_classes((AllowAny,))
# @csrf_exempt
# def getWebsiteBundlesForCategory(request):
#     slug = request.query_params.get('slug')
#     bundleSerialized = {}
#     try:
#         categoryObject = Category.objects.get(slug=slug)
#         bundlesQS = Bundle.objects.filter(categoryId=categoryObject)
#         bundleSerialized = BundleSerializer(bundlesQS,many=True).data
#     except Exception as e:
#             logger.error("Exception in getWebsiteBundlesForCategory: %s " %(str(e)))
#     return JsonResponse({'bundles':bundleSerialized,'slug':categoryObject.slug,'title':categoryObject.name,'metaUrl':categoryObject.metaUrl,'metaDescription':categoryObject.metaDescription,'metaTitle':categoryObject.metaTitle}, safe=False)
@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def getWebsiteBundlesForCategory(request):
    context = {}
    slug = request.query_params.get('slug')
    bundleSerialized = {}
    try:
        categoryObject = Category.objects.get(slug=slug)
        bundlesQS = Bundle.objects.filter(categoryId=categoryObject)
        bundleSerialized = BundleSerializer(bundlesQS,many=True).data
        result={'bundles':bundleSerialized,'slug':categoryObject.slug,'title':categoryObject.name,'metaUrl':categoryObject.metaUrl,'metaDescription':categoryObject.metaDescription,'metaTitle':categoryObject.metaTitle}
        context.update(result)

    except Category.DoesNotExist:
        result = {"ErrorCode": error_codes.ERROR, "ErrorMsg":"Category Does not Exist"}
        context.update(result)

        
    except Bundle.DoesNotExist:
        result = {"ErrorCode": error_codes.ERROR, "ErrorMsg":"Bundle Not Exist"}
        context.update(result)


    except Exception as e:
        logger.error("Exception in getWebsiteBundlesForCategory: %s " %(str(e)))
        result = {"ErrorCode": error_codes.ERROR, "ErrorMsg": "Server Error"}
        context.update(result)


    return JsonResponse({'result':context},safe=False)



@permission_classes((AllowAny,))
# @csrf_exempt
class getWebsitePagniatedBundlesForCategory(generics.ListCreateAPIView):
    # queryset = Category.objects.all()
    serializer_class = BundleSerializer
    pagination_class = BundleResultsSetPagination
    bundleSerialized = {}
    def get_queryset(self):
        # print("print in get queryset")
        slug = self.request.query_params['slug']
        # print(slug)
        categoryItemObject = {}
        try:
            categoryObject = Category.objects.get(slug=slug)
            itemList = []
            categoryItemObject = Bundle.objects.filter(categoryId=categoryObject)
            # bundleSerialized = BundleSerializer(categoryItemObject,many=True).data
        except Exception as e:
            logger.error("Exception in getWebsitePagniatedBundlesForCategory: %s " %(str(e)))
        return categoryItemObject

@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def getWebsiteBundleItemDetails(request):
    bundleSerialized = {}
    bundleItem = {}
    categoryObject = {}
    catName = None
    bundleType = None
    slug = request.data['slug']
    try:
        bundleObject = Bundle.objects.get(slug=slug)
        if bundleObject:
            bundleType = bundleObject.bundleType

            if bundleObject.bundleType == Bundle.BRAND:
                if bundleObject.categoryId_id != None:
                    categoryObject = Category.objects.get(id=bundleObject.categoryId_id)
                    if categoryObject:
                        catName = categoryObject.name
            else:
                catName = bundleObject.name
            bundleItem = list(BundleItem.objects.filter(bundleId=bundleObject).values('status').annotate(id=F('itemId__id'),stock=F('itemId__stock'),name=F('itemId__name'),qty=F('quantity'),image=F('itemId__image'),slug=F('itemId__slug'),sku=F('itemId__sku'), mrp=F('itemId__mrp'), salePrice=F('itemId__salePrice')).order_by('priority'))
            bundleSerialized = BundleSerializer(bundleObject).data
    except Exception as e:
            logger.error("Exception in getWebsiteBundleItemDetails: %s " %(str(e)))
    return JsonResponse({'bundleItems':bundleItem,"bundle":bundleSerialized,"category":catName, "bundleType":bundleType}, safe=False)

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
@is_admin
@csrf_exempt
def addBundleItem(request):
    context = {}
    bundle = request.data['data']
    id = request.data['id']
    logger.info("Request: %s" %(request.data))
    try:
        bundleObject = Bundle.objects.get(id=id)
        for item in bundle:
            itemObject = Item.objects.get(id=item['id'])
            BundleItem.objects.create(itemId=itemObject,quantity=item['quantity'],bundleId=bundleObject)
    except Exception as e:
            logger.error("Exception in addBundleItem: %s " %(str(e)))
    return JsonResponse(context, safe=False)

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
@is_admin
@csrf_exempt
def updateBundleItem(request):
    context = {}
    bundle = request.data['data']
    id = request.data['id']
    logger.info("Request: %s" %(request.data))
    try:
        bundleObject = Bundle.objects.get(id=id)
        oldItemList = list(BundleItem.objects.filter(bundleId = bundleObject).values('itemId'))
        oldItemList = [f['itemId'] for f in oldItemList]
        for item in bundle:
            creationFlag = True
            for oldListValue in oldItemList:
                if item['id'] == oldListValue:
                    creationFlag = False
                    BundleItem.objects.filter(bundleId = bundleObject, itemId=item['id']).update(quantity=item['quantity'])
                    oldItemList.remove(oldListValue)
            if(creationFlag):
                itemObject = Item.objects.get(id=item['id'])
                BundleItem.objects.create(itemId=itemObject,quantity=item['quantity'],bundleId=bundleObject)
        if(oldItemList):
            for value in oldItemList:
                # BundleItem.objects.filter(bundleId=bundleObject,id=item['id']).delete()
                bundleItemObject = BundleItem.objects.get(bundleId=bundleObject,itemId=value)
                bundleItemObject.delete()
            # if(BundleItem.objects.filter(bundleId=bundleObject,id=item['id']).exists()):
            #     if(item['status']==1):
            #         BundleItem.objects.filter(bundleId=bundleObject,id=item['id']).update(quantity=item['quantity'])
            #     else:
            #         BundleItem.objects.filter(bundleId=bundleObject,id=item['id']).delete()
            # else:
            #     itemObject = Item.objects.get(id=item['id'])
            #     BundleItem.objects.create(itemId=itemObject,quantity=item['quantity'],bundleId=bundleObject)
    except Exception as e:
            logger.error("Exception in updateBundleItem: %s " %(str(e)))
    
    return JsonResponse(context, safe=False)


# @method_decorator(api_view(["POST"]), name='dispatch')
@permission_classes((IsAuthenticated,))
# @method_decorator(is_admin, name='dispatch')
class addBrand(generics.CreateAPIView):
        # result = {}
        # http_method_names = ['POST','GET']
        queryset = Category.objects.all()
        serializer_class = CategorySerializer
        parser_classes = (MultiPartParser, FormParser)
        # permission_classes = [IsAuthenticated,]

# @method_decorator(api_view(["PUT", "PATCH"]), name='dispatch')
@permission_classes((IsAuthenticated,))
# @method_decorator(is_admin, name='dispatch')
class updateBrand(generics.UpdateAPIView):
        result = {}
        queryset = Category.objects.all()
        serializer_class = CategorySerializer
        parser_classes = (MultiPartParser, FormParser)
        permission_classes = [IsAuthenticated,]

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
@is_admin
@csrf_exempt
def deleteBrand(request):
        context = {}
        brandId = request.data
        logger.info("Request %s " %(str(request.data)))
        try:
            categoryObject = Category.objects.get(id=brandId)
            if(Bundle.objects.filter(categoryId=categoryObject).exists()):
                result = {"ErrorCode": error_codes.ERROR, "ErrorMsg": error_codes.SCHL_EXST_IN_BNDL_ERR_MSG}
            else:
                Category.objects.filter(id = brandId).delete()
                result = {"ErrorCode": error_codes.SUCCESS, "ErrorMsg": error_codes.DELETE_MSG}
            context.update(result)
            # logger.info("%s " %(str(result)))
        except Exception as e:
            result = {"ErrorCode": error_codes.ERROR, "ErrorMsg": error_codes.NOT_DELETE_MSG}
            context.update(result)
            # print("Exception in Delete Bundle View ", str(e))
            logger.error("Exception in deleteBrand: %s " %(str(e)))
            # traceback.print_exc()
        return JsonResponse(context, safe=False)

############### Admin ###################
@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
@is_admin
@csrf_exempt
def addAdmin(request):
        context = {}
        valueDict = request.data['valueDict']
        logger.info("Request %s" %(str(request.data)))
        try:
            if(User.objects.filter(email=valueDict['email']).exists()):
                result = {"ErrorCode": error_codes.ERROR, "ErrorMsg": error_codes.EMAIL_ALREADY_EXIST}
                context.update(result)
            else:
                obj = User()
                for (field, value) in (valueDict.items()):
                    if value:
                        if field=='password':
                            setattr(obj,field,make_password(value))
                        else:
                            setattr(obj, field,value)
                setattr(obj,'username',valueDict['email'])
                responseObject = obj.save()
                userSerialized = UserSerializer(responseObject).data
                result = {"ErrorCode": error_codes.SUCCESS, "ErrorMsg": error_codes.CREATE_MSG, "Add Admin":userSerialized}
                context.update(result)
                logger.info("%s" %(str(userSerialized)))
        except Exception as e:
            result = {"ErrorCode": error_codes.ERROR, "ErrorMsg": error_codes.NOT_ADD_MSG}
            context.update(result)
            print("Exception in Add Admin View ", str(e))
            logger.error("Exception in addAdmin: %s " %(str(e)))
            # traceback.print_exc()
        return JsonResponse(context, safe=False)

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
@is_admin
@csrf_exempt
def updateAdmin(request):
        context = {}
        valueDict = request.data['valueDict']
        logger.info("Request %s " %(str(request.data)))
        try:
            userObject = User.objects.filter(id=valueDict['id']).update(name=valueDict['name'],email=valueDict['email'],mobile=valueDict['mobile'],status=valueDict['status'])
            userSerialized = UserSerializer(userObject).data
            result = {"ErrorCode": error_codes.SUCCESS, "ErrorMsg": error_codes.UPDATE_MSG, "Update Admin":userSerialized}
            context.update(result)
            logger.info("%s " %(str(userSerialized)))
        except Exception as e:
            result = {"ErrorCode": error_codes.ERROR, "ErrorMsg": error_codes.NOT_UPDATE_MSG}
            context.update(result)
            print("Exception in Update Admin View ", str(e))
            logger.error("Exception in updateAdmin: %s " %(str(e)))
            # traceback.print_exc()
        return JsonResponse(context, safe=False)

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
@is_admin
@csrf_exempt
def updateAdminProfile(request):
        context = {}
        valueDict = request.data['valueDict']
        logger.info("Request %s " %(str(request.data)))
        try:
            userObject = User.objects.filter(id=valueDict['id']).update(name=valueDict['name'],mobile=valueDict['mobile'])
            userSerialized = UserSerializer(userObject).data
            result = {"ErrorCode": error_codes.SUCCESS, "ErrorMsg": error_codes.UPDATE_MSG, "Update Admin":userSerialized}
            context.update(result)
            logger.info("%s " %(str(userSerialized)))
        except Exception as e:
            result = {"ErrorCode": error_codes.ERROR, "ErrorMsg": error_codes.NOT_UPDATE_MSG}
            context.update(result)
            print("Exception in Update Admin Profile View ", str(e))
            logger.error("Exception in updateAdminProfile: %s " %(str(e)))
            # traceback.print_exc()
        return JsonResponse(context, safe=False)

# @method_decorator(api_view(["PUT", "PATCH"]), name='dispatch')
@permission_classes((IsAuthenticated,))
# @method_decorator(is_admin, name='dispatch')
class updateAdminImage(generics.UpdateAPIView):
        result = {}
        queryset = User.objects.all()
        serializer_class = UserSerializer
        parser_classes = (MultiPartParser, FormParser)
        permission_classes = [IsAuthenticated,]

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
@is_admin
@csrf_exempt
def deleteAdmin(request):
        context = {}
        userId = request.data['id']
        logger.info("Request %s " %(str(request.data)))
        try:
            # userObject = User.objects.filter(id=valueDict['id']).update(name=valueDict['name'],email=valueDict['email'],mobile=valueDict['mobile'],status=valueDict['status'])
            userObject = User.objects.filter(id = userId).delete()
            userSerialized = UserSerializer(userObject).data
            result = {"ErrorCode": error_codes.SUCCESS, "ErrorMsg": error_codes.DELETE_MSG, "Delete Admin":userSerialized}
            context.update(result)
            logger.info("%s " %(str(userSerialized)))
        except Exception as e:
            result = {"ErrorCode": error_codes.ERROR, "ErrorMsg": error_codes.NOT_DELETE_MSG}
            context.update(result)
            print("Exception in Delete Admin View ", str(e))
            logger.error("Exception in deleteAdmin: %s " %(str(e)))
            # traceback.print_exc()
        return JsonResponse(context, safe=False)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
@is_admin
def getAllAdmin(request):
    adminObject = {}
    try:
        adminObject = list(User.objects.filter(status=User.ACTIVE,role=User.ADMIN).values('id','name','email','username','phone','mobile','profile_pic','gender','address','role','status'))
    except Exception as e:
            logger.error("Exception in getAllAdmin: %s " %(str(e)))
    return JsonResponse(adminObject, safe=False)

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
@is_admin
@csrf_exempt
def getAdmin(request):
    adminObject = {}
    adminObject= {}
    adminId = request.data['id']
    try:
        adminObject = list(User.objects.filter(id=adminId).values('id','name','email','username','phone','mobile','gender','address','role','status','profile_pic').order_by('id'))
    except Exception as e:
            logger.error("Exception in getAdmin: %s " %(str(e)))
    return JsonResponse(adminObject, safe=False)


########## Customers #############
def syncCustomers(request):
    context = {'Key':'success'}
    className = class_for_name(customer_module_name, customer_class_name)
    syncObj = className()
    # extPos = request.pos
    extPos = 'Gofrugal_RPOS7'
    syncObj.syncCustomers()

    return JsonResponse(context)


############ Order ################
# @api_view(['GET', 'POST'])
# @permission_classes((AllowAny,))
# @csrf_exempt
# def addOrder(request):
#         result = {}
#         valueDict = request.data['valueDict']
#         cartList = request.data['cartList']
#         totalPrice = request.data['totalPrice']
#         totalItemQty = 0
#         date = datetime.date.today()
#         formatedDate = date.strftime("%Y""%m""%d")
        
#         try:
#             orderObj = Order.objects.create(custName=valueDict['name'], custEmail=valueDict['email'], custPhone=valueDict['phone'], cust_phone2=valueDict['phone2'], custCity=valueDict['city'], shippingAddress=valueDict['address'], shippingCity=valueDict['city'], totalBill=totalPrice, deliveryCharges=300, discountedBill=totalPrice, paymentMethod='COD')
#             # orderObject = Order.AddOrder(valueDict)
#             for cart in cartList:
#                 # print('In Cart List')
#                 totalItemQty = cart['qty'] + totalItemQty
#                 itemTotalPrice = cart['qty'] * cart['price']
#                 orderDescObj = OrderDescription.objects.create(item_type=1, itemSku=cart['sku'], itemName=cart['name'], itemUnit='each', itemMinQty=1,mrp=cart['mrp'],salePrice=cart['salePrice'],itemIndPrice=cart['price'], itemTotalPrice=itemTotalPrice, itemQty=cart['qty'], isStockManaged=True,order=orderObj)

#             Order.objects.filter(id=orderObj.pk).update(totalItems=totalItemQty,orderNo=str(formatedDate)+str(orderObj.pk))
#             orderSerialized = OrderSerializer(orderObj).data
#             # userSerialized = OrderSerializer(orderObj).data
#             result = {"addOrder":orderSerialized}
            
#         except Exception as e:
#             # result = {"ErrorCode": error_codes.ERROR, "ErrorMsg": error_codes.NOT_ADD_MSG}
#             print("Exception in Add Order View ", str(e))
#             # logger.error("Exception in addHostelRoom: %s " %(str(e)))
#             # traceback.print_exc()
#         # return result
#         return JsonResponse(result, safe=False)



@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def addOrder(request):
        context = {}
        shipObj={}
        valueDict = request.data['valueDict']
        userid=request.data['userid']
        cartList = request.data['cartList']
        totalPrice = request.data['totalPrice']
        deliveryfee = request.data['deliveryFee']

        totalItemQty = 0
        name=valueDict['name']
        logger.info("Request: %s" %(request.data))
        date = datetime.date.today()
        formatedDate = date.strftime("%Y""%m""%d")
        sh=UserShippingDetail.objects.filter(user=userid,area=valueDict['city'],city=valueDict['city'],address=valueDict['address']).values()
        try:
            orderObj = Order.objects.create(custId=userid,custName=valueDict['name'], custEmail=valueDict['email'], custPhone=valueDict['phone'], cust_phone2=valueDict['phone2'], custCity=valueDict['city'], shippingAddress=valueDict['address'], shippingCity=valueDict['city'], totalBill=totalPrice, deliveryCharges=deliveryfee, discountedBill=totalPrice, paymentMethod='COD')
            formatedOrderNo = str(formatedDate)+str(orderObj.pk)  
            if(User.objects.filter(id=userid).exists()):
                if sh.exists():
                    shipObj={}
                else:
                    shipObj=   UserShippingDetail.objects.create(user=User.objects.get(id=userid),area=valueDict['city'],city=valueDict['city'],address=valueDict['address'])
            else:
                shipObj=   UserShippingDetail.objects.create(area=valueDict['city'],city=valueDict['city'],address=valueDict['address'])
            for cart in cartList:
                # print('In Cart List')
                totalItemQty = cart['qty'] + totalItemQty
                itemTotalPrice = cart['qty'] * cart['price']
                orderDescObj = OrderDescription.objects.create(item_type=1, itemSku=cart['sku'], itemName=cart['name'], itemUnit='each', itemMinQty=1,mrp=cart['mrp'],salePrice=cart['salePrice'],itemIndPrice=cart['price'], itemTotalPrice=itemTotalPrice, itemQty=cart['qty'], isStockManaged=True,order=orderObj)

            Order.objects.filter(id=orderObj.pk).update(totalItems=totalItemQty,orderNo=formatedOrderNo)
            OrderObject = Order.objects.get(id=orderObj.id)
            orderno=Order.objects.values('orderNo')
            orderSerialized = OrderSerializer(OrderObject).data
            shipSerialized=ShippingSerializers(shipObj).data
            order=orderSerialized
            ship=[order]
            detail=order
            host=HostDomain
            sitesetting=SiteSettings.objects.values()

            sitesettingname = sitesetting[0]

            sitename = sitesettingname['site_name']

            imageurl=ImageUrl
          

            context = {"addOrder":orderSerialized,"ship":shipSerialized}

            subject = f"{sitename} Order #{formatedOrderNo} - Order Confirmation"
            email_template = 'email_template.html'
            message = f'{context}'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [valueDict['email'], ]
            email_body = render_to_string(email_template,{'ship':ship,'order':cartList,'detail':detail,'host':host,'sitesetting':sitesetting,'imageurl':ImageUrl})
           
            msg = EmailMultiAlternatives(subject=subject, from_email=email_from,
                             to=recipient_list, body=email_body)
            msg.attach_alternative(email_body, "text/html")
            msg.send()
            result = {"ErrorCode": error_codes.SUCCESS, "ErrorMsg": "Order Added Successfully"}
            context.update(result)
        
        except Exception as e:
            result = {"ErrorCode": error_codes.ERROR, "ErrorMsg": "Order Not Added "}
         
            context.update(result)
            # result = {"ErrorCode": error_codes.ERROR, "ErrorMsg": error_codes.NOT_ADD_MSG}
            print("Exception in Add Order View ", str(e))
            logger.error("Exception in addOrder: %s " %(str(e)))
            # traceback.print_exc()
        # return result
     
       
        return JsonResponse(context, safe=False)

# @api_view(['GET', 'POST'])
# @permission_classes((IsAuthenticated,))
# @csrf_exempt
# def getAllOrder(request):
#     orderObject = {}
#     try:
#         orderObject = list(Order.objects.filter().values('id','orderNo','totalBill','totalItems','timestamp','shippingAddress','status'))
#     except Exception as e:
#             logger.error("Exception in getAllOrder: %s " %(str(e)))
#     return JsonResponse(orderObject, safe=False)

# @method_decorator(api_view(["GET", "POST"]), name='dispatch')
@permission_classes((IsAuthenticated,))
# @method_decorator(is_admin, name='dispatch')
class getAllOrder(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    queryset = Order.objects.filter().order_by('-timestamp')
    pagination_class = CustomResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['orderNo','custName','custPhone','shippingAddress','shippingCity','timestamp','status']

def getAllOrderNotification(request):
    orderNotificationObject = {}
    try:
        orderNotificationObject = list(Order.objects.filter(orderNotification=0).values('custName','timestamp','orderNo','id').order_by('-timestamp'))
    except Exception as e:
            logger.error("Exception in getAllOrderNotification: %s " %(str(e)))
    return JsonResponse(orderNotificationObject, safe=False)

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
@is_admin
@csrf_exempt
def getOrderProduct(request):
    returnList = []
    orderNo = request.data['orderNo']
    try:
        orderObject = Order.objects.get(orderNo = orderNo)
        orderDescObject = OrderDescription.objects.filter(order=orderObject)
        for product in orderDescObject:
            itemObject = Item.objects.filter(sku=product.itemSku).values('image','isbn')
            # print(itemObject[0]['image'])
            productList = {'id':product.id,'name':product.itemName,'image':itemObject[0]['image'],'isbn':itemObject[0]['isbn'],'price':product.itemIndPrice,'totalPrice':product.itemTotalPrice,'sku':product.itemSku,'qty':product.itemQty,'mrp':product.mrp,'salePrice':product.salePrice, 'isDeleted':product.isDeleted} 
            returnList.append(productList)
    except Exception as e:
            print("Exception in getOrderProducts: ",e)
            logger.error("Exception in getOrderProduct: %s " %(str(e)))
    return JsonResponse(returnList, safe=False)

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
@is_admin
@csrf_exempt
def getOrder(request):
    orderObject = {}
    orderNo = request.data['orderNo']
    try:
        orderObject = list(Order.objects.filter(orderNo = orderNo).values('id','orderNo','custName','custEmail','custPhone','cust_phone2','custCity','shippingAddress','shippingCity','totalBill','discountedBill','deliveryCharges','totalItems','paymentMethod','timestamp','status','orderNotification','paymentstatus','paymentid','paymenttime','customeronlinepaymentinvoice'))
    except Exception as e:
            logger.error("Exception in getOrder: %s " %(str(e)))
    return JsonResponse(orderObject, safe=False)

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
@is_admin
@csrf_exempt
def seenOrderNotification(request):
    context = {}
    logger.info("Request: %s" %(request.data))
    orderNo = request.data['orderNo']
    try:
        orderObject = Order.objects.filter(orderNo=orderNo).update(orderNotification=1)
        result = {"ErrorCode": error_codes.SUCCESS, "ErrorMsg": error_codes.ORDR_NOTIFCTN_SEEN_SUCCESS_MSG}
        context.update(result)
        # orderObject = list(Order.objects.filter(orderNo = orderNo).values('id','orderNo','custName','custEmail','custPhone','cust_phone2','custCity','shippingAddress','shippingCity','totalBill','discountedBill','deliveryCharges','totalItems','paymentMethod','timestamp','status','orderNotification'))
    except Exception as e:
            result = {"ErrorCode": error_codes.ERROR, "ErrorMsg": error_codes.ORDR_NOTIFCTN_SEEN_ERROR_MSG}
            context.update(result)
            logger.error("Exception in seenOrderNotification: %s " %(str(e)))
    return JsonResponse(context, safe=False)


@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
@is_admin
@csrf_exempt
def updateOrder(request):
        context = {}
        logger.info("%s " %(str(request.data)))
        status = request.data['status']
        shippingAddress = request.data['shippingAddress']
        deliveryCharges = request.data['deliveryCharges']
        totalBill = request.data['totalBill']
        deletedProduct = request.data['deletedProduct']
        orderNo = request.data['orderNo']
        updatedProduct = request.data['updatedProduct']
        totalItemQty = 0
        logger.info("Request: %s" %(request.data))
        try:
            orderObj = Order.objects.get(orderNo=orderNo)
            orderSerialized = OrderSerializer(orderObj).data
            if(status=='PENDING'):
                Order.objects.filter(orderNo=orderNo).update(deliveryCharges=deliveryCharges,totalBill=totalBill,discountedBill=totalBill)
            else:
                if(status=='CANCELLED'):
                    subject = f"IdrisBookBank Order #{orderNo} - Order Cancelled"
                    email_template = 'order_cancel_template.html'
                    email_from = settings.EMAIL_HOST_USER
                    recipient_list = [orderObj.custEmail, ]
                    email_body = render_to_string(email_template,{'detail':orderSerialized})

                    msg = EmailMultiAlternatives(subject=subject, from_email=email_from,
                                    to=recipient_list, body=email_body)
                    msg.attach_alternative(email_body, "text/html")
                    msg.send()   
                Order.objects.filter(orderNo=orderNo).update(deliveryCharges=deliveryCharges,totalBill=totalBill,discountedBill=totalBill,status=status)
            for update in updatedProduct:
                totalItemQty = int(update['qty']) + totalItemQty
                if "id" in update:
                    OrderDescription.objects.filter(order=orderObj,id=update['id']).update(itemQty=update['qty'],itemTotalPrice=Decimal(update['price'])*int(update['qty']))
                else:
                    itemTotalPrice = int(update['qty']) * Decimal(update['price'])
                    OrderDescription.objects.create(item_type=1, itemSku=update['sku'], itemName=update['name'], itemUnit='each', itemMinQty=1,mrp=update['mrp'],salePrice=update['salePrice'],itemIndPrice=update['price'], itemTotalPrice=itemTotalPrice, itemQty=update['qty'], isStockManaged=True,order=orderObj)
            for delete in deletedProduct:
                OrderDescription.objects.get(id=delete['id']).delete()

            Order.objects.filter(id=orderObj.pk).update(totalItems=totalItemQty,shippingAddress=shippingAddress)
            logger.info("%s " %(str(orderSerialized)))
            result = {"ErrorCode": error_codes.SUCCESS, "ErrorMsg": error_codes.UPDATE_MSG, "updateOrder":orderSerialized}
            context.update(result)
            
        except Exception as e:
            result = {"ErrorCode": error_codes.ERROR, "ErrorMsg": error_codes.NOT_UPDATE_MSG}
            context.update(result)
            print("Exception in Update Order View ", str(e))
            logger.error("Exception in updateOrder: %s " %(str(e)))
            # traceback.print_exc()
        return JsonResponse(context, safe=False)

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
# @is_admin
@csrf_exempt
def getOrderSentToPosDetails(request):
    context = {}
    orderNo = request.data['orderNo']
    logger.info("Request: %s" %(request.data))
    # orderNo = 2022112315
    try:
        orderObject = Order.objects.get(orderNo=orderNo)
        NumOfItems = OrderDescription.objects.filter(order=orderObject).count()
        returnList = {
            "salesOrder":{ 
            "onlineReferenceNo":orderObject.orderNo,
            "createdAt":str(currentDateTime.now()),
            "status":"pending",
            "totalQuantity":orderObject.totalItems,
            "totalAmount":str(orderObject.totalBill),
            "paymentMode":"COD",
            "totalTaxAmount":0.0000,
            "totalDiscountAmount":0.0,
            "shippingId":orderObject.orderNo,
            "shippingName":orderObject.custName,
            "shippingAddress1":orderObject.shippingAddress,
            "shippingCountry":"Pakistan",
            "shippingCharge":str(orderObject.deliveryCharges),
            "shippingPincode":"0",
            "shippingMobile":orderObject.cust_phone2,
            "shippingEmail":orderObject.custEmail,
            "shippingStateCode": 0,
            "shipmentItems":NumOfItems,
            "customerName":orderObject.custName,
            "customerAddressLine1":orderObject.shippingAddress,
            "customerCountry": "Pakistan",
            "customerCity":orderObject.shippingCity,
            "customerMobile":orderObject.cust_phone2,
            "customerPhone":orderObject.custPhone,
            "customerEmail":orderObject.custEmail,
            "Channel":"E-Commerce API"
            }}
        child =[]
        
        orderDetailObject = OrderDescription.objects.filter(order=orderObject).values('id','itemSku','itemName','mrp','salePrice','itemIndPrice','itemTotalPrice','itemQty')
        for index,record in enumerate(orderDetailObject):
            orderDetailList = {'rowNo':index+1,'itemId':record['itemSku'],'itemName':record['itemName'],'itemReferenceCode':record['itemSku'],'salePrice':str(record['salePrice']),'quantity':record['itemQty'],'itemAmount':str(record['mrp']),'taxPercentage':0.0}
            child.append(orderDetailList)
        returnList['salesOrder']['orderItems'] = child
        r=requests.post("https://722157.true-order.com/WebReporter/api/v1/salesOrders",data = json.dumps(returnList), headers={"X-Auth-Token":"9BAA1E819AD48254DFF928F5012BBD95585D2E068EC93AED4DA0810AC0D649BE35F51CE2432EA204"})
        json_data = r.json()
        if 'result' in json_data:
            if(json_data['result']['status'] == "success"):
                Order.objects.filter(orderNo=orderNo).update(status='PENDING',orderPKPos=json_data['result']['id'])
                result = {"ErrorCode": error_codes.SUCCESS, "ErrorMsg": error_codes.UPDATE_MSG}
                context.update(result)
        else:
            if 'error' in json_data:
                if(json_data['error']['code'] == 4414):
                    result = {"ErrorCode": error_codes.ERROR, "ErrorMsg": json_data['error']['message']}
                    context.update(result)
                elif(json_data['error']['code'] == 4422):
                    result = {"ErrorCode": error_codes.ERROR, "ErrorMsg": json_data['error']['message']}
                    context.update(result)
                logger.error("error from POS: %s" %(result))
    except Exception as e:
            result = {"ErrorCode": error_codes.ERROR, "ErrorMsg": error_codes.NOT_SENT_TO_POS_MSG}
            context.update(result)
            logger.error("Exception in getOrderSentToPosDetails: %s " %(str(e)))
    return JsonResponse(context, safe=False)


################# ZUHOOR VIEWS #####################
#############Save to DB##########################
@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
# @is_admin
@csrf_exempt
def saveOrderDB(request):
    context = {}
    orderNo = request.data['orderNo']
    logger.info("Request: %s" %(request.data))
    # orderNo = 2022112315
    try:
        orderObject = Order.objects.get(orderNo=orderNo)
        NumOfItems = OrderDescription.objects.filter(order=orderObject).count()
        
        child =[]
        
        orderDetailObject = OrderDescription.objects.filter(order=orderObject).values('id','itemSku','itemName','mrp','salePrice','itemIndPrice','itemTotalPrice','itemQty')
        for index,record in enumerate(orderDetailObject):
            orderDetailList = {'rowNo':index+1,'itemId':record['itemSku'],'itemName':record['itemName'],'itemReferenceCode':record['itemSku'],'salePrice':str(record['salePrice']),'quantity':record['itemQty'],'itemAmount':str(record['mrp']),'taxPercentage':0.0}
            child.append(orderDetailList)
            
            Order.objects.filter(orderNo=orderNo).update(status='CONFIRMED')
            
            item = Item.objects.get(sku=record['itemSku'])
            item.stock -= record['itemQty']

            item.save()
            
            result = {"ErrorCode": error_codes.SUCCESS, "ErrorMsg": error_codes.UPDATE_MSG}
            context.update(result)
    
    except Exception as e:
            result = {"ErrorCode": error_codes.ERROR, "ErrorMsg": error_codes.NOT_SENT_TO_POS_MSG}
            context.update(result)
            logger.error("Exception in getOrderSentToDB: %s " %(str(e)))
    return JsonResponse(context, safe=False)












# def saveOrderDB(request):
#     context = {}
#     orderNo = request.data['orderNo']
#     logger.info("Request: %s" %(request.data))
#     # orderNo = 2022112315
#     try:
#         orderObject = Order.objects.get(orderNo=orderNo)
#         NumOfItems = OrderDescription.objects.filter(order=orderObject).count()
        
#         child =[]
        
#         orderDetailObject = OrderDescription.objects.filter(order=orderObject).values('id','itemSku','itemName','mrp','salePrice','itemIndPrice','itemTotalPrice','itemQty')
#         for index,record in enumerate(orderDetailObject):
#             orderDetailList = {'rowNo':index+1,'itemId':record['itemSku'],'itemName':record['itemName'],'itemReferenceCode':record['itemSku'],'salePrice':str(record['salePrice']),'quantity':record['itemQty'],'itemAmount':str(record['mrp']),'taxPercentage':0.0}
#             child.append(orderDetailList)
#             Order.objects.filter(orderNo=orderNo).update(status='CONFIRMED')
#             result = {"ErrorCode": error_codes.SUCCESS, "ErrorMsg": error_codes.UPDATE_MSG}
#             context.update(result)
    
#     except Exception as e:
#             result = {"ErrorCode": error_codes.ERROR, "ErrorMsg": error_codes.NOT_SENT_TO_POS_MSG}
#             context.update(result)
#             logger.error("Exception in getOrderSentToDB: %s " %(str(e)))
#     return JsonResponse(context, safe=False)


############### Section Sequence ################

@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def getFeaturedItems(request):
    serialized_data = {}
    try:
        type = request.GET.get('type', 'new')  
        filter_kwargs = {'status': Item.ACTIVE}
        
        if type == 'new':
            filter_kwargs['isNewArrival'] = True
        elif type == 'featured':
            filter_kwargs['isFeatured'] = True
        
        featureObject = Item.objects.filter(**filter_kwargs).order_by("-newArrivalTill", "-isFeatured", "-stock")[:20]
        serialized_data = ItemSerializer(featureObject, many=True).data
    except Exception as e:
        logger.error("Exception in getFeaturedItems: %s" % str(e))
        return JsonResponse({'error': 'An error occurred'}, status=500)
    
    return JsonResponse(serialized_data, safe=False, status=200)


@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
@csrf_exempt
def getCustomerOrder(request):
    orderObject = {}
    id = request.data['id']
    try:
        orderObject = list(Order.objects.filter(custId=id).values())
    except Exception as e:
            logger.error("Exception in getCustomerOrder: %s " %(str(e)))
    return JsonResponse(orderObject, safe=False)

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
@csrf_exempt
def getCustomerOrdersDes(request):
    orderObject = {}
    id = request.data['id']
    try:
        orderObject = list(OrderDescription.objects.filter(order_id=id).values())
    except Exception as e:
            logger.error("Exception in getCustomerOrdersDes: %s " %(str(e)))
    return JsonResponse(orderObject, safe=False)

@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def getOrderDetails(request):
    orderObject = {}
    id = request.data['id']
    try:
        orderObject = list(Order.objects.filter(id=id).values())
    except Exception as e:
            logger.error("Exception in getOrderDetails: %s " %(str(e)))
    return JsonResponse(orderObject, safe=False)

@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def getItemSearchCategory(request):
    serialized_data = {}
    slug = request.data['id']
    try:
        categoryObject = Category.objects.get(slug=slug)    
        categoryItemList = list(CategoryItem.objects.filter(categoryId=categoryObject).values_list("itemId",flat=True))
        
        items = Item.objects.filter(id__in= categoryItemList,status=Item.ACTIVE,isFeatured=True).order_by('-stock',"-newArrivalTill")[:20]
        serialized_data =ItemSerializer(items, many=True).data
    except Exception as e:
            logger.error("Exception in getItemSearchCategory: %s " %(str(e)))
    return JsonResponse(serialized_data, safe=False)


def getAllSectionSequence(request):
    itemObject = {}
    try:
        itemObject = list(SectionSequence.objects.values())
    except Exception as e:
            logger.error("Exception in getAllSectionSequence: %s " %(str(e)))
    return JsonResponse(itemObject, safe=False)

@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def addSectionSequence(request):
        result = {}
        id=request.data['id']
        sequenceNo=request.data['sequenceNo']
        category=request.data['category'] 
        child1=request.data['child1'] 
        child1name=request.data['child1_name'] 
        child1slug=request.data['child1_slug'] 
        child2=request.data['child2']  
        child2name=request.data['child2_name'] 
        child2slug=request.data['child2_slug'] 
        child3=request.data['child3'] 
        child3name=request.data['child3_name'] 
        child3slug=request.data['child3_slug']  
        child4=request.data['child4']  
        child4name=request.data['child4_name'] 
        child4slug=request.data['child4_slug'] 
        child5=request.data['child5']  
        child5name=request.data['child5_name'] 
        child5slug=request.data['child5_slug'] 
        child6=request.data['child6']  
        child6name=request.data['child6_name'] 
        child6slug=request.data['child6_slug'] 
        child7=request.data['child7']  
        child7name=request.data['child7_name'] 
        child7slug=request.data['child7_slug'] 
        child8=request.data['child8']  
        child8name=request.data['child8_name'] 
        child8slug=request.data['child8_slug']  
        category_slug=request.data['category_slug']    
        categoryObj=Category.objects.get(id=category)
        child1Obj=Category.objects.get(id=child1)
        child2Obj=Category.objects.get(id=child2)
        child3Obj=Category.objects.get(id=child3)
        child4Obj=Category.objects.get(id=child4)
        child5Obj=Category.objects.get(id=child5)
        child6Obj=Category.objects.get(id=child6)
        child7Obj=Category.objects.get(id=child7)
        child8Obj=Category.objects.get(id=child8)
        name=request.data['name']

        valueDict={
            'id':id,
            'sequenceNo':sequenceNo,'child1':child1Obj,
            'child2':child2Obj,'child3':child3Obj,'child4':child4Obj,
            'child5':child5Obj,'child6':child6Obj,'child7':child7Obj,
            'child8':child8Obj,'child1_name':child1name,'child1_slug':child1slug,
            'child2_name':child2name,'child2_slug':child2slug,
            'child3_name':child3name,'child3_slug':child3slug,
            'child4_name':child4name,'child4_slug':child4slug,
            'child5_name':child5name,'child5_slug':child5slug,
            'child6_name':child6name,'child6_slug':child6slug,
            'child7_name':child7name,'child7_slug':child7slug,
            'child8_name':child8name,'child8_slug':child8slug,
            'category':categoryObj,'category_slug':category_slug,
            'name':name
            }
        try: 
            sectionObject =SectionSequence.AddSectionSequence(valueDict)
            sectionSerialized =SectionSequenceSerializer(sectionObject).data
            result = {"SectionSerialized":sectionSerialized}   
        except Exception as e:
            logger.error("Exception in addSectionSequence: %s " %(str(e)))
            traceback.print_exc()
            # print("Exception in Section ", str(e))
        return JsonResponse(result, safe=False)

############### Individual DETAIL ################

@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def addIndividualBoxOrder(request):
        result = {}
        id=request.data['id']
        sequenceNo=request.data['sequenceNo']
        image=request.data['image']
        category=request.data['category']       
        categoryObj=Category.objects.get(id=category)
        category_slug=request.data['category_slug']
        name=request.data['name']
        logger.info("Request: %s" %(request.data))
        valueDict={
            'id':id,
            'sequenceNo':sequenceNo,'image':image,
            'category':categoryObj,'category_slug':category_slug,'name':name}   
        try:
            
            individualObject = IndividualBoxOrder.Addindorder(valueDict)
            individualSerialized = IndividualBoxOrderSerializer(individualObject).data
            result = {"addindividualSerialized":individualSerialized}
        except Exception as e:
            logger.error("Exception in addIndividualBoxOrder: %s " %(str(e)))
            traceback.print_exc()
            # print("Exception in Individual ", str(e))
           
        return JsonResponse(result, safe=False)

def getAllIndividualOrder(request):
    itemObject = {}
    try:
        itemObject = list(IndividualBoxOrder.objects.values())
    except Exception as e:
            logger.error("Exception in getAllIndividualOrder: %s " %(str(e)))
    
    return JsonResponse(itemObject, safe=False)

################### WISHLIST ##################

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
@csrf_exempt
def updateWishlist(request):
    result = {}
    try:
        logger.info("Request: %s" %(request.data))
        userid=request.data['userid']
        itemid = request.data['itemid']
        wishListObject=Wishlist.objects.filter(user_id=int(userid), item_id=int(itemid))
        if wishListObject:
            wishListObject.delete()
        else:
            wishObject=Wishlist.objects.create(user_id=userid,item_id=itemid)
    except Exception as e:
        logger.error("Exception in updateWishlist: %s " %(str(e)))
        # print("Exception in update Wishlist View ", str(e))
    return JsonResponse("Sucessfully added", safe=False)

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
@csrf_exempt
def getWishlist(request):
    wishListObject = {}
    userid=request.user.id
    try:
        wishListObject=list(Wishlist.objects.filter(user_id=userid).values_list('item_id',flat=True))
    except Exception as e:
        logger.error("Exception in getWishlist: %s " %(str(e)))
    return JsonResponse(wishListObject, safe=False)

################### SHIPPING DETAILS ############

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
def getCustomerShipping(request):
    userShippingobj = {}
    userFkey=request.data['id']
    try:
        userShippingobj = list(UserShippingDetail.objects.filter(user=userFkey).values('id','city','address','area','house','user').order_by('id'))
    except Exception as e:
        logger.error("Exception in getCustomerShipping: %s " %(str(e)))
   
    return JsonResponse(userShippingobj, safe=False)

# NEW UPDATES 

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
def deleteCustomerShipping(request):
    deleteuserShippingobj = {} 
    userFkey=request.data['id']
    sid = request.data['shipping']
    logger.info("Request: %s" %(request.data))
    try:
        deleteuserShippingobj = UserShippingDetail.objects.filter(user=userFkey,id=sid).delete()
    except Exception as e:
        logger.error("Exception in deleteCustomerShipping: %s " %(str(e)))
    return JsonResponse(deleteuserShippingobj, safe=False)

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
def cusGetWishlists(request):
    userlist = {} 
    userFkey=request.data['id']
    try:
        userWishlistobj = Wishlist.objects.filter(user=userFkey).values('item_id')
        # userlist=list(Item.objects.filter(id__in=userWishlistobj).values())
        userlist = list(Item.objects.filter(id__in=userWishlistobj).values('id','author','description','isbn','isFeatured','isNewArrival','newArrivalTill','length','name','mrp','salePrice','sku', 'image','slug','status','stock','timestamp','weight','width','weightGrams')
        )
    except Exception as e:
        print(e)
        logger.error("Exception in cusGetWishlists: %s " %(str(e)))
    return JsonResponse(userlist, safe=False) 
@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
def GetWishlists(request):
    userlist = {} 
    userFkey=request.data['id']
    try:
        userWishlistobj = Wishlist.objects.filter(user=userFkey).values('item_id')
        userlist=list(Item.objects.filter(id__in=userWishlistobj).values('id'))
    except Exception as e:
        logger.error("Exception in cusGetWishlists: %s " %(str(e)))
    return JsonResponse(userlist, safe=False) 

################## BUNDELS ZUHOOR ###############

class PostListDetailfilter(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = Item.objects.all()
    serializer_class =ItemSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def getBrandBundels(request):
    bundelSerialized = {}
    try:
        bundleid=list(Bundle.objects.filter(bundleType="BRAND").values_list("categoryId",flat=True))
        cid=Category.objects.filter(id__in=bundleid).order_by('priority')
        bundelSerialized = CategorySerializer(cid,many=True).data
    except Exception as e:
        logger.error("Exception in getBrandBundels: %s " %(str(e)))

    return JsonResponse(bundelSerialized, safe=False)
@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def getProductBundels(request):
    bundelSerialized = {}
    try:
        bundleid=Bundle.objects.filter(bundleType="PRODUCT",status=Bundle.ACTIVE).order_by('priority')
        bundelSerialized = BundleSerializer(bundleid,many=True).data
    except Exception as e:
        logger.error("Exception in getProductBundels: %s " %(str(e)))
    return JsonResponse(bundelSerialized, safe=False)

@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def getBundels(request):
    bundelSerialized = {}
    try:
        bundelList =Bundle.objects.values()
        bundelSerialized = BundleSerializer(bundelList,many=True).data
    except Exception as e:
        logger.error("Exception in getBundels: %s " %(str(e)))
    return JsonResponse(bundelSerialized, safe=False)

@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
def registerUser(request):
    context = {}
    name=request.data['fullName']
    email=request.data['email']
    password=request.data['password']
    phone=request.data['phone']
    address=request.data['address']
    logger.info("Request: %s" %(request.data))
    try:
        if(User.objects.filter(email=email).exists()):
            result = {"ErrorCode": error_codes.ERROR, "ErrorMsg": error_codes.EMAIL_ALREADY_EXIST}
            context.update(result)
        else:
            createuser = User.objects.create(username=email,email=email,password=make_password(password),phone=phone,address=address,name=name)
            result = {"ErrorCode": error_codes.SUCCESS, "ErrorMsg": error_codes.CREATE_MSG}
            context.update(result)
           
    except Exception as e:
        result = {"ErrorCode": error_codes.ERROR, "ErrorMsg": error_codes.NOT_ADD_MSG}
        context.update(result)
        logger.error("Exception in registerUser: %s " %(str(e)))
            # traceback.print_exc()
    # print(context)
    return JsonResponse(context, safe=False)


@permission_classes((AllowAny,))
class getAllWebsitePaginatedItem(generics.ListCreateAPIView):
    serializer_class = ItemSerializer
    pagination_class = AdminResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'slug','sku','author','isbn','manufacturer']

    def get_queryset(self):
        itemObject = {}
        try:
            itemObject = Item.objects.filter(appliesOnline=1,status=Item.ACTIVE).order_by("-newArrivalTill","-isFeatured","-stock")
        except Exception as e:
            logger.error("Exception in getAllWebsitePaginatedItem: %s " %(str(e)))
        return itemObject

from django.core.paginator import Paginator
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector,TrigramSimilarity

# @api_view(['GET', 'POST'])
# @permission_classes((AllowAny,))
# @csrf_exempt
# def get_all_website_paginated_item(request):
#     print(request)
#     search = request.GET.get('search', '')
#     search = search.replace("-"," ")
#     page = request.GET.get('page', 1)
#     data = {}
#     page_size = request.GET.get('pageSize', 9)
#     logger.info("Product Query: %s" %(search))
#     try:
#         products = Item.objects.annotate(similarity=TrigramSimilarity(
#               'name', search
#             ) + TrigramSimilarity(
#               'author', search
#             )+ TrigramSimilarity(
#               'manufacturer', search
#             )).filter(status=Item.ACTIVE,similarity__gte=0.3).order_by('-similarity',"-stock","-newArrivalTill","-isFeatured")
#         paginator = Paginator(products, page_size)
#         page_obj = paginator.get_page(page)

#         serializer = ItemSerializer(page_obj, many=True)
#         data = {
#             'results': serializer.data,
#             'count': paginator.count
#         }
#     except Exception as e:
#         logger.error("Exception in get_all_website_paginated_item: %s " %(str(e)))
#         print("Exception: ",e)
#     return Response(data)

@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
@csrf_exempt

# from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
def get_all_website_paginated_item(request):
    # print(request)
    search = request.GET.get('search', '')
    search = search.replace("-", " ")
    page = request.GET.get('page', 1)
    data = {}
    page_size = request.GET.get('pageSize', 9)
    sort_option = request.GET.get('sort', '')  
    logger.info("Product Query: %s" % (search))
    
    try:
        vector = SearchVector('name', 'author', 'manufacturer')
        query = SearchQuery(search)
        words = search.split()
        condition = Q()
        for word in words:
            condition &= Q(name__icontains=word)
        # Get the items that match the search query
        # searched_items = Item.objects.annotate(rank=SearchRank(vector, query)).filter(
        #     condition,
        #     status=Item.ACTIVE
        # ).order_by('-rank')

        # Get the items that are similar to the search query
        # similar_items = Item.objects.annotate(rank=SearchRank(vector, query),similarity=TrigramSimilarity('name', search)+ TrigramSimilarity('author', search) + TrigramSimilarity('manufacturer', search)).filter(status=Item.ACTIVE).order_by('-rank','-similarity')
        items = Item.objects.annotate(
            rank=Case(
                When(condition, then=SearchRank(vector, query)),
                default=Value(0),
                output_field=models.FloatField(),
            ),
            rank2=Case(
                When(condition, then=SearchRank(vector, query)),
                default=Value(0.7),
                output_field=models.FloatField(),
            ),
            similarity=Case(
                When(condition, then=Value(1.0)),  # Set similarity to 1 for items that match the search query
                default=TrigramSimilarity('name', search) + TrigramSimilarity('author', search) + TrigramSimilarity('manufacturer', search),
                output_field=models.FloatField(),
            ),
        ).filter(Q(rank__gte=0.4) | Q(rank2__gte=0.6) | Q(similarity__gt=0.6),status=Item.ACTIVE).order_by('-rank','-rank2', '-similarity')
        # Combine the searched items and similar items
        products =items
    
        # Order the products based on relevance, similarity, and rank
        # products = products.order_by(
        #     Case(
        #         When(Q(name__icontains=search), then=Value(0)),
        #         default=Value(1),
        #         output_field=IntegerField()
        #     ),
        #     '-rank'
        # )
        if sort_option == 'asc':
            products = products.order_by('salePrice') 
        elif sort_option == 'desc':
            products = products.order_by('-salePrice')  

        paginator = Paginator(products, page_size)
        page_obj = paginator.get_page(page)

        serializer = ItemSerializer(page_obj, many=True)
        data = {
            'results': serializer.data,
            'count': paginator.count
        }
    except Exception as e:
        logger.error("Exception in get_all_website_paginated_item: %s " % (str(e)))
        print("Exception: ", e)
    
    return Response(data)



# def get_all_website_paginated_item(request):
#     search = request.GET.get('search', '')
#     search = search.replace("-", " ")
#     page = request.GET.get('page', 1)
#     data = {}
#     page_size = request.GET.get('pageSize', 9)
#     sort_option = request.GET.get('sort', '')  
#     logger.info("Product Query: %s" % (search))
#     print(("Product Query: %s" % (search)))
    
#     try:
#         vector = SearchVector('name', 'author', 'manufacturer')
#         query = SearchQuery(search)

        
#         products = Item.objects.annotate(search=vector).filter(
#             search=query, status=Item.ACTIVE
#         )
#         products |= Item.objects.annotate(similarity=TrigramSimilarity('name', search)+ TrigramSimilarity('author', search) + TrigramSimilarity('manufacturer', search)).filter(status=Item.ACTIVE, similarity__gte=0.3).order_by('-similarity')


#         products=products.order_by('-newArrivalTill', '-isFeatured', '-stock')

#         if sort_option == 'asc':
#             products = products.order_by('salePrice', '-newArrivalTill', '-isFeatured', '-stock') 
#         elif sort_option == 'desc':
#             products = products.order_by('-salePrice', '-newArrivalTill', '-isFeatured', '-stock')  

#         paginator = Paginator(products, page_size)
#         page_obj = paginator.get_page(page)

#         serializer = ItemSerializer(page_obj, many=True)
#         data = {
#             'results': serializer.data,
#             'count': paginator.count
#         }
#     except Exception as e:
#         logger.error("Exception in get_all_website_paginated_item: %s " % (str(e)))
#         print("Exception: ", e)
    
#     return Response(data)


# def get_all_website_paginated_item(request):
#     search = request.GET.get('search', '')
#     search = search.replace("-", " ")
#     page = request.GET.get('page', 1)
#     data = {}
#     page_size = request.GET.get('pageSize', 9)
#     sort_option = request.GET.get('sort', '')
    
#     try:
#         products = Item.objects.filter(status=Item.ACTIVE)
        
#         if search:
#             products = products.annotate(similarity=TrigramSimilarity(
#                 'name', search
#             ) + TrigramSimilarity(
#                 'author', search
#             ) + TrigramSimilarity(
#                 'manufacturer', search
#             )).filter(similarity__gte=0.1).order_by('-similarity', "-newArrivalTill", "-isFeatured", "-stock")
#             # query = Q(name__icontains=search) | Q(author__icontains=search) | Q(manufacturer__icontains=search)
#             # products = Item.objects.filter(status=Item.ACTIVE).filter(query).order_by("-newArrivalTill", "-isFeatured", "-stock")

#         else:
#             products = products.order_by("-newArrivalTill", "-isFeatured", "-stock")
        
#         if sort_option == 'asc':
#             products = products.order_by("salePrice", "-newArrivalTill", "-isFeatured", "-stock") 
#         elif sort_option == 'desc':
#             products = products.order_by("-salePrice", "-newArrivalTill", "-isFeatured", "-stock")
        
#         paginator = Paginator(products, page_size)
#         page_obj = paginator.get_page(page)

#         serializer = ItemSerializer(page_obj, many=True)
#         data = {
#             'results': serializer.data,
#             'count': paginator.count
#         }
#     except Exception as e:
#         logger.error("Exception in get_all_website_paginated_item: %s" % str(e))
#         print("Exception:", e)

#     return Response(data)


@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def resetpassword(request):
    if request.method == 'POST':
        email=request.data['email']
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
      return JsonResponse({'message': 'No user with that email address'}, status=400)
   
    token = default_token_generator.make_token(user)
    uid = user_pk_to_url_str(user)
    reset_password_link = f'{HostDomain}reset-password?uid={uid}&token={token}'
 
    subject = 'Welcome To IdrisBookBank'
    email_from = EMAIL_HOST_USER
    recipient_list = [email, ]
    email_body = f'Click this link to reset your password: {reset_password_link}'
    msg = EmailMultiAlternatives(subject=subject, from_email=email_from,
                        to=recipient_list, body=email_body)
    msg.attach_alternative(email_body, "text/html")
    msg.send()
    return JsonResponse({'message': 'Password reset email sent'})

# ==========================================================homePage=====================================================================
from django.core.serializers import serialize

# @api_view(['GET', 'POST'])
@api_view(['GET'])
@permission_classes((AllowAny,))
@csrf_exempt
def AllIndividualBoxOrder(request):
    boxOrderItem = {}
    try:
        boxOrderItem=list(Individual_BoxOrder.objects.values().order_by('id'))
        # print(boxOrderItem)
    except Exception as e:
        logger.error("Exception in AllIndividualBoxOrder: %s " %(str(e)))
    return JsonResponse(boxOrderItem, safe=False)

@api_view(['GET'])
@permission_classes((AllowAny,))
@csrf_exempt
def AllCategories(request):
    categoryObject = {}
    try:
        categoryObject = list(Category.objects.values('id','icon','slug','name','parentId_id','isBrand'))
        # categorySerialized = CategorySerializer(categoryObject, many=True).data
        # context = {"categories": categoryObject}
    except Exception as e:
        logger.error("Exception in AllCategories: %s " %(str(e)))
    return JsonResponse(categoryObject, safe=False)

@api_view(['GET'])
@permission_classes((AllowAny,))
@csrf_exempt
def AllSectionSequence(request):
    itemObject = {}
    try:
        itemObject = list(SectionSequence.objects.values())
        # print(itemObject)
    except Exception as e:
        logger.error("Exception in AllSectionSequence: %s " %(str(e)))
    return JsonResponse(itemObject, safe=False)

@api_view(['GET'])
@permission_classes((AllowAny,))
@csrf_exempt
def AllConfiguration(request):
    ConfigurationObject = {}
    try:
        ConfigurationObject = list(Configuration.objects.values())
        # print(ConfigurationObject)
    except Exception as e:
        logger.error("Exception in ConfigurationObject: %s " %(str(e)))
    return JsonResponse(ConfigurationObject, safe=False)

@api_view(['POST'])
@permission_classes((IsSuperAdmin,))
@csrf_exempt
def addConfiguration(request):
        result = {}
        # print(request.data)
        # id=request.data['id']
        name=request.data['name']
        value=request.data['value']
        location=request.data['location']       
        priority=request.data['priority']
        try:
            Configuration.objects.create(name=name, value=value, location=location, priority=priority)
        except Exception as e:
            traceback.print_exc()
            print("Exception in addConfiguration ", str(e))
            logger.error("Exception: %s" %(str(e)))
        return JsonResponse(result, safe=False)

class updateConfiguration(generics.UpdateAPIView):
    queryset = Configuration.objects.all()
    serializer_class = ConfigurationSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (IsSuperAdmin,)

@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def getConfiguration(request):
    ConfigurationObject = {}
    # print(request.data)
    id = request.data['id']
    try:
        ConfigurationObject = list(Configuration.objects.filter(id=id).values())
    except Exception as e:
        logger.error("Exception in getConfiguration: %s " %(str(e)))
    return JsonResponse(ConfigurationObject, safe=False)


@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def checkConfigurationChange(request):
    result = {}
    data = request.data
    logger.info("Request: %s" %(request.data))
    try:
        if(Configuration.objects.filter(id=data['id']).exists()):
            ConfigurationObject = Configuration.objects.filter(id=data['id']).update(name=data['name'], value=data['value'], location=data['location'], priority=data['priority'])
        result = {"ErrorCode": error_codes.SUCCESS, "ErrorMsg": error_codes.SUCCESS_MSG}
    except Exception as e:
        logger.error("Exception in checkConfigurationChange: %s " %(str(e)))
        result = {"ErrorCode": error_codes.ERROR, "ErrorMsg": error_codes.ERROR_MSG}
    # print("ConfigurationObject: ", ConfigurationObject)
    return JsonResponse(result, safe=False)

@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def addIndividual_BoxOrder(request):
        result = {}
        # print(request.data)
        category=request.data['id']
        image=request.data['icon']
        category_slug=request.data['slug']
        name=request.data['name']
        logger.info("Request: %s" %(request.data))
        try:
            IndividualBoxOrder.objects.update(image=image, category=category, category_slug=category_slug, name=name)
            # IndividualBoxOrder.objects.update_or_create(image=image, category=category, category_slug=category_slug, name=name)
        except Exception as e:
            traceback.print_exc()
            print("Exception in Individual ", str(e))
            logger.error("Exception in addIndividual_BoxOrder: %s " %(str(e)))
        return JsonResponse(result, safe=False)


@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def IndividualBoxOrder_Post(request):
        result = {}
        # print(request.data)
        # id=request.data['id']
        sequenceNo=request.data['sequenceNo']
        image=request.data['image']
        category_slug=request.data['category_slug']
        category_name=request.data['name']
        type=request.data['type']
        parent=request.data['parent']
        category_id=request.data['id']
        logger.info("Request: %s" %(request.data))
        try:
            Individual_BoxOrder.objects.create(sequenceNo=sequenceNo, image=image, category_slug=category_slug, category_name=category_name, type=type, parent=parent, category_id=category_id)

        except Exception as e:
            traceback.print_exc()
            print("Exception in Individual_BoxOrder ", str(e))
            logger.error("Exception in IndividualBoxOrder_Post: %s " %(str(e)))
        return JsonResponse(result, safe=False)


@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def IndividualBoxOrder_Update(request):
    result={}
    allData=request.data
    logger.info("Request: %s" %(request.data))
    try:
        noOfSections = int(Configuration.objects.filter(name='section').values_list('value', flat=True).first())
        noOfBoxes = int(Configuration.objects.filter(name='box').values_list('value', flat=True).first())    
        SectionIndex=0
        for index, data in enumerate(allData):
            if (data['type'] == 'box'):
                boxCount_table = Individual_BoxOrder.objects.filter(type=data['type']) #count no. of boxes in table
                if (len(boxCount_table) != noOfBoxes): # diff length
                    boxCount_table = Individual_BoxOrder.objects.filter(type=data['type'])
                    if(len(boxCount_table) > noOfBoxes): # more values in table
                        try:
                            deleteBox= len(boxCount_table) - noOfBoxes #delete extra
                            for i in range(deleteBox):
                                Individual_BoxOrder.objects.filter(sequenceNo=(len(boxCount_table))-i, type = "box").delete()
                        except Exception as e:
                            traceback.print_exc()
                            print("Exception in Delete (Box) ", str(e))
                        Individual_BoxOrder.objects.filter(sequenceNo=index+1, type=data['type']).update(category_id=data['id'], category_name=data['name'], image=data['image'], category_slug=data['category_slug'], parent=data['parent']) #update the first item
                    else: # if old values are less than new values
                            checkBox = Individual_BoxOrder.objects.filter(sequenceNo=index+1, type=data['type']).update(category_id=data['id'], category_name=data['name'], image=data['image'], category_slug=data['category_slug'], parent=data['parent'])
                            if (checkBox == 0):
                                category = Category.objects.get(id=data['id'])
                                Individual_BoxOrder.objects.create(sequenceNo=index+1, category_id=category, category_name=data['name'], image=data['image'], category_slug=data['category_slug'], type=data['type'])
                            else:
                                pass
                else: # if length is equal
                    if Individual_BoxOrder.objects.filter(category_id=data['id'], type=data['type']): # if no change
                        pass
                    else: #if values are updated
                        Individual_BoxOrder.objects.filter(sequenceNo=index+1, type=data['type']).update(category_id=data['id'], category_name=data['name'], image=data['image'], category_slug=data['category_slug'], parent=data['parent'])
            else:   # if section data
                SectionIndex = SectionIndex+1 #sequenceNo
                if (SectionIndex <= noOfSections):
                    new_parentId = data['id'] # new section id
                    checkSwap = Individual_BoxOrder.objects.filter(type = 'section', category_id=new_parentId) #queryset where parent id is same
                    if checkSwap.exists():
                        # check if the sequenceNo is same
                        checkSequence = checkSwap.filter(sequenceNo = SectionIndex)
                        if checkSequence.exists():
                            pass
                        else:
                            #get sequenceNo
                            #swap sequenceNo of both parent
                            #books 1, textbooks 2
                            #this id exists in table at diff sequence
                            #get diff sequence, replace with current. 2 => 1
                            #get values from table at sequence 1. replace. 2 => 1  
                            getSequence2 =   Individual_BoxOrder.objects.filter(type = 'section', category_id=new_parentId).values_list('sequenceNo', flat=True).first()
                            Individual_BoxOrder.objects.filter(type = 'section', sequenceNo=SectionIndex).update(sequenceNo=getSequence2)
                            Individual_BoxOrder.objects.filter(type = 'section', category_id=new_parentId).update(sequenceNo=SectionIndex)
                    old_parentId = Individual_BoxOrder.objects.filter(type = 'section', sequenceNo=SectionIndex).values_list('category_id', flat=True).first() #in orignal table //old values
                    noOfSubcat_Table= Individual_BoxOrder.objects.filter(type = 'section_subcategory', parent=old_parentId) #old subcategories //8 subcategories data
                    compareSections = Individual_BoxOrder.objects.filter(sequenceNo=data['sequenceNo'], type = 'section', category_id=new_parentId)
                    sectionCount_table = Individual_BoxOrder.objects.filter(type='section') # no of sections in table
                    if (len(sectionCount_table) != noOfSections): #if new and old values are not equal 
                        sectionCount_table = Individual_BoxOrder.objects.filter(type='section')
                        if (len(sectionCount_table) > noOfSections): # if old values are more than new
                            try:
                                deleteSection= len(sectionCount_table) - noOfSections #no. of sections to be deleted
                                for i in range(deleteSection):
                                    parentID = Individual_BoxOrder.objects.filter(sequenceNo=(len(sectionCount_table))-i, type = "section").values_list('category_id', flat=True).first() 
                                    Individual_BoxOrder.objects.filter(sequenceNo=(len(sectionCount_table))-i, type = "section").delete()
                                    count = Individual_BoxOrder.objects.filter(type = "section_subcategory", parent=parentID)
                                    for i in range(len(count)): #delete all subcategories
                                        Individual_BoxOrder.objects.filter(sequenceNo=i+1, type = "section_subcategory", parent=parentID).delete()
                                        
                            except Exception as e:
                                traceback.print_exc()
                                print("Exception in Delete (Box) ", str(e))
                            Individual_BoxOrder.objects.filter(sequenceNo=SectionIndex, type=data['type']).update(category_id=data['id'], category_name=data['name'], image=data['image'], category_slug=data['category_slug'], parent=data['parent'])
                        else:
                            pass
                    if compareSections.exists(): #if section is not updated
                        for ind_subcategories, subcategories in enumerate(data['subCategories'][0]):
                            #check if subcategories are updated
                            noOfSubcat_Table = Individual_BoxOrder.objects.filter(type='section_subcategory', parent=old_parentId) | Individual_BoxOrder.objects.filter(type='section_subcategory', parent=new_parentId)
                            if len(noOfSubcat_Table) != len(data['subCategories'][0]): # if length of old != new sub categories
                                if len(noOfSubcat_Table) > len(data['subCategories'][0]): #table values > new
                                    try:
                                        delete= len(noOfSubcat_Table) - len(data['subCategories'][0])
                                        for i in range(delete):
                                            Individual_BoxOrder.objects.filter(sequenceNo=(len(noOfSubcat_Table))-i, type = "section_subcategory", parent=old_parentId).delete()
                                    except Exception as e:
                                        traceback.print_exc()
                                        print("Exception in Delete ", str(e))
            
                                    Individual_BoxOrder.objects.filter(sequenceNo=ind_subcategories+1, type=subcategories['type'], parent=old_parentId).update(category_id=subcategories['id'], category_name=subcategories['name'], image=subcategories['image'], category_slug=subcategories['category_slug'], parent=subcategories['parent'])
                                else: #table values < new
                                        category = Category.objects.get(id=subcategories['id'])
                                        try:
                                            create= len(data['subCategories'][0]) - len(noOfSubcat_Table)
                                            for i in range(create):
                                                Individual_BoxOrder.objects.create(sequenceNo=(len(data['subCategories'][0]))-i, category_id=category, category_name=subcategories['name'], image=subcategories['image'], category_slug=subcategories['category_slug'], parent=old_parentId, type=subcategories['type'])
                            
                                        except Exception as e:
                                            traceback.print_exc()
                                            print("Exception in create ", str(e))
                                        Individual_BoxOrder.objects.filter(sequenceNo=ind_subcategories+1, type=subcategories['type'], parent=old_parentId).update(category_id=subcategories['id'], category_name=subcategories['name'], image=subcategories['image'], category_slug=subcategories['category_slug'], parent=subcategories['parent'])
                            else:
                                compareSub = Individual_BoxOrder.objects.filter(sequenceNo=ind_subcategories+1, type='section_subcategory', category_id=subcategories['id'])
                                if compareSub.exists():
                                    pass
                                else:
                                    Individual_BoxOrder.objects.filter(sequenceNo=ind_subcategories+1, type=subcategories['type'], parent=new_parentId).update(category_id=subcategories['id'], category_name=subcategories['name'], image=subcategories['image'], category_slug=subcategories['category_slug'])
                    else: #section updated
                        checkSection = Individual_BoxOrder.objects.filter(sequenceNo=SectionIndex, type=data['type']).update(category_id=data['id'], category_name=data['name'], image=data['image'], category_slug=data['category_slug'])
                        if (checkSection == 0):
                            category = Category.objects.get(id=data['id'])
                            Individual_BoxOrder.objects.create(sequenceNo=SectionIndex ,category_id=category, category_name=data['name'], image=data['image'], category_slug=data['category_slug'], type=data['type'])
                        else:
                            pass
                        #update subcategories
                        for ind_subcategories, subcategories in enumerate(data['subCategories'][0]):
                            noOfSubcat_Table = Individual_BoxOrder.objects.filter(type='section_subcategory', parent=old_parentId) | Individual_BoxOrder.objects.filter(type='section_subcategory', parent=new_parentId)

                            if len(noOfSubcat_Table) != len(data['subCategories'][0]): # if length of old != new sub categories
                                if len(noOfSubcat_Table) > len(data['subCategories'][0]):
                                    try:
                                        delete= len(noOfSubcat_Table) - len(data['subCategories'][0])
                                        for i in range(delete):
                                            Individual_BoxOrder.objects.filter(sequenceNo=(len(noOfSubcat_Table))-i, type = "section_subcategory", parent=old_parentId).delete()
                                    except Exception as e:
                                        traceback.print_exc()
                                        print("Exception in Delete ", str(e))
            
                                    Individual_BoxOrder.objects.filter(sequenceNo=ind_subcategories+1, type=subcategories['type'], parent=old_parentId).update(category_id=subcategories['id'], category_name=subcategories['name'], image=subcategories['image'], category_slug=subcategories['category_slug'], parent=subcategories['parent'])
                                else:
                                    category = Category.objects.get(id=subcategories['id'])
                                    try:
                                        create= len(data['subCategories'][0]) - len(noOfSubcat_Table)
                                        for i in range(create):
                                            Individual_BoxOrder.objects.create(sequenceNo=(len(data['subCategories'][0]))-i, category_id=category, category_name=subcategories['name'], image=subcategories['image'], category_slug=subcategories['category_slug'], parent=old_parentId, type=subcategories['type'])
                        
                                    except Exception as e:
                                        traceback.print_exc()
                                        print("Exception in create ", str(e))
                                    Individual_BoxOrder.objects.filter(sequenceNo=ind_subcategories+1, type=subcategories['type'], parent=old_parentId).update(category_id=subcategories['id'], category_name=subcategories['name'], image=subcategories['image'], category_slug=subcategories['category_slug'], parent=subcategories['parent'])
                            else:
                                    Individual_BoxOrder.objects.filter(sequenceNo=ind_subcategories+1, type=subcategories['type'], parent=old_parentId).update(category_id=subcategories['id'], category_name=subcategories['name'], image=subcategories['image'], category_slug=subcategories['category_slug'], parent=subcategories['parent'])
                    old_parentId = 0
                else:
                    pass
    except Exception as e:
        logger.error("Exception in IndividualBoxOrder_Update: %s " %(str(e)))
    return JsonResponse(result, safe=False)

# ==============================================================================================================================================


@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def BoxOrder(request):
    itemObject = {}
    try:
        itemObject = list(Individual_BoxOrder.objects.values())
    except Exception as e:
        logger.error("Exception in BoxOrder: %s " %(str(e)))
    return JsonResponse(itemObject, safe=False)

# ======================================   Sync Images of Items from Bucket  ===============================================================================================
from django.core.exceptions import ObjectDoesNotExist
def SetDefaultItemImage():
    # items = Item.objects.filter(image='item_image/default-item-image.jpg').update(image='default-item-image.jpg')
    items = Item.objects.filter(image='default-item-image.jpg').update(image='idris/asset/default-item-image.jpg')


def SyncObjectStorageItemImages():
    linode_obj_config = {
        "aws_access_key_id": env('AWS_ACCESS_KEY_ID'),
        "aws_secret_access_key": env('AWS_SECRET_ACCESS_KEY'),
        "endpoint_url": env('AWS_S3_CUSTOM_DOMAIN'),
    }
    client = boto3.client("s3", **linode_obj_config)
    itemPrefix = 'idris/asset/'
    deletePrefix = 'deleted/idris/asset/'
    defaultImage ='idris/asset/default-item-image.jpg'
    excepCount = 0
    exceptionImages = []
    deleteImages = []
    try:
        confValue = Configuration.objects.get(name="last_sync_time_item_images")
        if confValue:
            # 1900-03-02 00:00:00+00:00
            last_sync_time = Configuration.objects.filter(name="last_sync_time_item_images").values_list('value',flat=True).first()
            last_sync_time=datetime.datetime.fromisoformat(last_sync_time)
    except ObjectDoesNotExist:
        try:
            last_sync_time = datetime.datetime(1900, 3, 2, 0, 0, 0, tzinfo=datetime.timezone.utc)
            Configuration.objects.create(name="last_sync_time_item_images",value=last_sync_time)
        except Exception as e:
            logger.error("Configuration for last_sync_time_item_images not created: %s " %(str(e)))
    

    paginator = client.get_paginator('list_objects_v2')
    deletedPages = paginator.paginate(Bucket=env('AWS_STORAGE_BUCKET_NAME'), Prefix=deletePrefix)
    for page in deletedPages:
        for object in page['Contents']:
            # print("objects is : ",object)
            if object['LastModified'] > last_sync_time:
                if '(' in object['Key']:
                    logger.error("Invalid image name, cannot process it. Delete it %s: %s" %(object['Key'],"Invalid naming convention"))
                    deleteImages.append(object['Key'])
                    excepCount = excepCount+1
                elif "_" in object['Key']:
                    # print("Gallery image: ",object['Key'])
                    imageNameWithoutPrefix = object['Key'].split(deletePrefix)
                    # print("imageNameWithoutPrefix: ",imageNameWithoutPrefix)
                    itemId = imageNameWithoutPrefix[1].split("_")
                    # print("itemId: ",itemId)
                    try:
                        item = Item.objects.get(extPosId=int(itemId[0]))
                        # print(item)
                        if item:
                            imageName = object['Key'].split(".")
                            # print("imageName: ",imageName)
                            galleryItems = ItemGallery.objects.filter(itemId=item)
                            # print("galleryItems: ",galleryItems)
                            if galleryItems:
                                for gItem in galleryItems:
                                    # print("gItem.image: ",gItem.image)
                                    # print("gItem.image.name: ",gItem.image.name)
                                    if imageNameWithoutPrefix[1] in gItem.image.name:
                                        gItem.delete()
                                        logger.info("Image deleted : %s " %(str(object['Key'])))
                                        # print("Deleted a gallery image")
                    except ObjectDoesNotExist:
                        # print("Image for said item does not exist: deleting ...")
                        deleteImages.append(object['Key'])
                        logger.error("Image for this item does not exist: delete it %s: " %(object['Key']))
                    except Exception as e:
                        # print("Delete Image Exception: ",object['Key'], ". Exception: ",e)
                        excepCount = excepCount+1
                        exceptionImages.append(object['Key'])
                        logger.error("Exception in processing this image %s: %s " %(object['Key'],str(e)))
                        pass
                else:
                    # print("single item image: ",object['Key'])
                    if object['Key'] == deletePrefix:
                        print("root object")
                    else:
                        imageKey = object['Key'].split(".")
                        imageName = imageKey[0].split(deletePrefix)
                        # print(imageName)
                        try:
                            item = Item.objects.get(extPosId=int(imageName[1]))
                            if item:
                                item.image = defaultImage
                                item.save()
                        except ObjectDoesNotExist:
                            # print("Image for said item does not exist: deleting ...")
                            logger.error("Image for this item does not exist: delete it %s: " %(object['Key']))
                            deleteImages.append(object['Key'])
                        except Exception as e:
                            # print("Delete Image Exception: ",object['Key'], ". Exception: ",e)
                            logger.error("Exception in processing this image %s: %s " %(object['Key'],str(e)))
                            excepCount = excepCount+1
                            exceptionImages.append(object['Key'])
                            pass
    # print("objects in this bucket")
    paginator = client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=env('AWS_STORAGE_BUCKET_NAME'), Prefix=itemPrefix)
    
    # print("Total pages ",(pages))
    for page in pages:
        for object in page['Contents']:
            if object['LastModified'] > last_sync_time:
                if '(' in object['Key']:
                    logger.error("Invalid image name, cannot process it. Delete it %s: %s" %(object['Key'],"Invalid naming convention"))
                    deleteImages.append(object['Key'])
                    excepCount = excepCount+1
                if "_" in object['Key']:
                    print("Gallery image: ",object['Key'])
                    imageNameWithoutPrefix = object['Key'].split(itemPrefix)
                    print("imageNameWithoutPrefix: ",imageNameWithoutPrefix)
                    itemId = imageNameWithoutPrefix[1].split("_")
                    print("itemId: ",itemId)
                    try:
                        item = Item.objects.get(extPosId=int(itemId[0]))
                        print(item)
                        if item:
                            imageName = object['Key'].split(".")
                            print("imageName: ",imageName)
                            galleryItems = ItemGallery.objects.filter(itemId=item)
                            print("galleryItems: ",galleryItems)
                            found = False
                            if galleryItems:
                                for gItem in galleryItems:
                                    print("gItem: ",gItem)
                                    print("gItem: ",gItem.image.name)
                                    if imageName[0] in gItem.image.name:
                                        gItem.image = object['Key']
                                        gItem.save()
                                        found=True
                                        break
                                    
                            if found == False:
                                # print("create new gallery item")
                                ItemGallery.objects.create(itemId=item,image=object['Key'])
                    except Exception as e:
                        # print("Exception: ",object['Key'], ". Exception: ",e)
                        excepCount = excepCount+1
                        deleteImages.append(object['Key'])
                        pass
                else:
                    # print("single item image")
                    imageKey = object['Key'].split(".")
                    imageName = imageKey[0].split(itemPrefix)
                    # print(imageName)
                    try:
                        item = Item.objects.get(extPosId=int(imageName[1]))
                        if item:
                            item.image = object['Key']
                            item.save()
                    except Exception as e:
                        # print("item does not exist in db : ",object['Key'], ". Exception: ",e)
                        excepCount = excepCount+1
                        deleteImages.append(object['Key'])
                        pass
    # print("Total exceptions: ",excepCount )
    logger.info("Delete Images : %s" %(deleteImages))
    logger.info("Exception in Images : %s" %(exceptionImages))
    subject = 'Image Processing Status'
    email_template = 's3_email_template.html'
    message = f'{context}'
    email_from = EMAIL_HOST_USER
    # recipient_list = env("IMAGE_PROCESSING_RECIPIENTS")
    recipient_list = IMAGE_PROCESSING_RECIPIENTS
    email_body = render_to_string(email_template,{'deleteImages':deleteImages,'exceptionImages':exceptionImages})
    
    msg = EmailMultiAlternatives(subject=subject, from_email=email_from,
                        to=recipient_list, body=email_body)
    msg.attach_alternative(email_body, "text/html")
    msg.send()

    if excepCount == 0:
        Configuration.objects.filter(name="last_sync_time_item_images").update(value=datetime.datetime.now(pytz.utc))
    return JsonResponse({"ErrorMsg":"Success"}, safe=False)

########## SiteMap Functions ##############

########## SiteMap Functions ##############


def DynamicSiteMapGenerator():
    try:
        linode_obj_config = {
            "aws_access_key_id": env('AWS_ACCESS_KEY_ID'),
            "aws_secret_access_key": env('AWS_SECRET_ACCESS_KEY'),
            "endpoint_url": env('AWS_S3_CUSTOM_DOMAIN'),
        }
        client = boto3.client("s3", **linode_obj_config)
        itemObject      = list(Item.objects.filter(status=Item.ACTIVE,appliesOnline=1).values_list('slug',flat=True))
        categoryObject  = list(Category.objects.filter(status=Category.ACTIVE,isBrand=False).values_list('slug',flat=True))
        bundleObject    = list(Bundle.objects.filter(status=Bundle.ACTIVE).values_list('slug',flat=True))
        brandObject    = list(Category.objects.filter(status=Category.ACTIVE,isBrand=True).values_list('slug',flat=True))

        _url = HostDomain  # <-- Your website domain.
        dt = datetime.datetime.now().strftime("%Y-%m-%d")  # <-- Get current date and time.
        schema_loc = ("http://www.sitemaps.org/schemas/sitemap/0.9 "
                    "http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd")

        root = ET.Element("urlset")
        root.attrib['xmlns:xsi'] = 'http://www.w3.org/2001/XMLSchema-instance'
        root.attrib['xsi:schemaLocation'] = schema_loc
        root.attrib['xmlns'] = "http://www.sitemaps.org/schemas/sitemap/0.9"

        doc = ET.SubElement(root, "url")
        ET.SubElement(doc, "loc").text = _url
        ET.SubElement(doc, "lastmod").text = dt
        ET.SubElement(doc, "changefreq").text = 'daily'
        ET.SubElement(doc, "priority").text = "1.0"

        doc = ET.SubElement(root, "url")
        ET.SubElement(doc, "loc").text = (f"{_url}login")
        ET.SubElement(doc, "lastmod").text = dt
        ET.SubElement(doc, "changefreq").text = 'weekly'
        ET.SubElement(doc, "priority").text = "0.6"

        for product in itemObject:
            doc = ET.SubElement(root, "url")
            ET.SubElement(doc, "loc").text = f"{_url}product/{product}"
            ET.SubElement(doc, "lastmod").text = dt
            ET.SubElement(doc, "changefreq").text = 'weekly'
            ET.SubElement(doc, "priority").text = "0.8"

        for category in categoryObject:
            doc = ET.SubElement(root, "url")
            ET.SubElement(doc, "loc").text = f"{_url}category/{category}"
            ET.SubElement(doc, "lastmod").text = dt
            ET.SubElement(doc, "changefreq").text = 'weekly'
            ET.SubElement(doc, "priority").text = "0.8"

        for bundle in bundleObject:
            doc = ET.SubElement(root, "url")
            ET.SubElement(doc, "loc").text = f"{_url}bundle/{bundle}"
            ET.SubElement(doc, "lastmod").text = dt
            ET.SubElement(doc, "changefreq").text = 'weekly'
            ET.SubElement(doc, "priority").text = "0.8"

        for brand in brandObject:
            doc = ET.SubElement(root, "url")
            ET.SubElement(doc, "loc").text = f"{_url}brand/{brand}"
            ET.SubElement(doc, "lastmod").text = dt
            ET.SubElement(doc, "changefreq").text = 'weekly'
            ET.SubElement(doc, "priority").text = "0.8"
                
        doc = ET.SubElement(root, "url")
        ET.SubElement(doc, "loc").text = f"{_url}signup"
        ET.SubElement(doc, "lastmod").text = dt
        ET.SubElement(doc, "changefreq").text = 'weekly'
        ET.SubElement(doc, "priority").text = "0.6"

        doc = ET.SubElement(root, "url")
        ET.SubElement(doc, "loc").text = (f"{_url}return-policy")
        ET.SubElement(doc, "lastmod").text = dt
        ET.SubElement(doc, "changefreq").text = 'weekly'
        ET.SubElement(doc, "priority").text = "0.6"

        doc = ET.SubElement(root, "url")
        ET.SubElement(doc, "loc").text = (f"{_url}about-us")
        ET.SubElement(doc, "lastmod").text = dt
        ET.SubElement(doc, "changefreq").text = 'weekly'
        ET.SubElement(doc, "priority").text = "0.6"

        doc = ET.SubElement(root, "url")
        ET.SubElement(doc, "loc").text = (f"{_url}privacy-policy")
        ET.SubElement(doc, "lastmod").text = dt
        ET.SubElement(doc, "changefreq").text = 'weekly'
        ET.SubElement(doc, "priority").text = "0.6"

        doc = ET.SubElement(root, "url")
        ET.SubElement(doc, "loc").text = (f"{_url}contact-us")
        ET.SubElement(doc, "lastmod").text = dt
        ET.SubElement(doc, "changefreq").text = 'weekly'
        ET.SubElement(doc, "priority").text = "0.6"
    
        tree = ET.ElementTree(root)
        tree.write(DEFAULT_SITEMAP_LOCAL,
                    encoding='utf-8', xml_declaration=True)
        client.upload_file(         
            Filename=DEFAULT_SITEMAP_LOCAL,
            Bucket=env('AWS_STORAGE_BUCKET_NAME'),
            Key=DEFAULT_SITEMAP_S3,
            ExtraArgs={'ACL':'public-read'})
    except Exception as e:
        logger.error("Exception in DynamicSiteMapGenerator: %s " %(str(e)))
    
def ResetIsNewArrival():
    try:
        Item.objects.filter(newArrivalTill__lte = currentDateTime.now()).update(isNewArrival=False,newArrivalTill=None)
        logger.info("Items reset that surpassed new arrival till date")
    except Exception as e:
        print("Exception in ResetIsNewArrival:",str(e))
        logger.error("Exception in ResetIsNewArrival: %s " %(str(e)))

    
def PublisherFlag():
    publisherCat = ['text-books','books']
    subCat = []
    try:
        confValue = Configuration.objects.filter(name="publisher_parentcategory")
        if confValue:
            publisherCat = list(Configuration.objects.filter(name="publisher_parentcategory").values_list('value',flat=True))
        else:
            Configuration.objects.create(name="publisher_parentcategory",value='text-books',priority=1)
            Configuration.objects.create(name="publisher_parentcategory",value='books',priority=2)
        subCat = publisherCat

        # print("first cat print: ",subCat)
        # for cat in subCat:
        #     print()
        #     parent = Category.objects.get(slug=cat)
        #     subCat.append(list(Category.objects.filter(parentId=parent).values_list('slug',flat=True)))
    except Exception as e:
        print(e)
        logger.error("Configuration for publisher_parentcategory : %s " %(str(e)))
    print(subCat)
    return subCat

def getSlidersFromCloud(request):
    linode_obj_config = {
        "aws_access_key_id": env('AWS_ACCESS_KEY_ID'),
        "aws_secret_access_key": env('AWS_SECRET_ACCESS_KEY'),
        "endpoint_url": env('AWS_S3_CUSTOM_DOMAIN'),
    }
    client = boto3.client("s3", **linode_obj_config)
    sliderPrefix = 'idris/sliders/'
    slidersList = []
    unwantedData = ['Thumbs.db',sliderPrefix]
    try:
        paginator = client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=env('AWS_STORAGE_BUCKET_NAME'), Prefix=sliderPrefix)
        for page in pages:
            for object in page['Contents']:
                if object['Key'] not in unwantedData:
                    slidersList.append(env('AWS_BASE_URL')+object['Key'])
    except Exception as e:
        print(e)
        logger.error("getSlidersFromCloud : %s " %(str(e)))
    return JsonResponse(slidersList, safe=False)


@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
@is_admin
@csrf_exempt
def adddynamictext(request):
   
    title = request.data['title']
    status = request.data['status']
    content = request.data['content']
    entry = DynamicText.objects.create(key=title,status=status, value=content)
    return JsonResponse({'message': 'Form submitted successfully'},)


@api_view(['GET'])
@permission_classes((AllowAny,))
def get_dynamic_text(request):
    key = request.GET.get('key')  
    dynamic_text = DynamicText.objects.filter(key=key)
    serializer = DynamicTextSerializer(dynamic_text, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
@is_admin
@csrf_exempt
def get_all_dynamic_text(request):
    dynamic_text = DynamicText.objects.all()
    serializer = DynamicTextSerializer(dynamic_text, many=True)
    return Response(serializer.data)


@api_view(['GET', 'POST','PUT'])
@permission_classes((IsAuthenticated,))
@is_admin
@csrf_exempt
def update_dynamic_text(request):

    dynamic_text_id = request.data['id']
    key = request.data['key']
    value = request.data['value']
    status = request.data['status']

    try:
        dynamic_text = DynamicText.objects.get(id=dynamic_text_id)
    except DynamicText.DoesNotExist:
        return JsonResponse({'error': 'Dynamic text does not exist'}, status=404)

    dynamic_text.key = key
    dynamic_text.value = value
    dynamic_text.status = status
    dynamic_text.save()

    return JsonResponse({'message': 'Dynamic text updated successfully'})

@permission_classes((IsAuthenticated,))
@api_view(['GET', 'POST','PUT'])
@is_admin
@csrf_exempt
def delete_dynamic_text(request):
    dynamic_text_id = request.data['id']

    try:
        dynamic_text = DynamicText.objects.get(id=dynamic_text_id)
        dynamic_text.delete()
        return JsonResponse({'message': 'DynamicText deleted successfully.'}, status=200)
    except DynamicText.DoesNotExist:
        return JsonResponse({'error': 'DynamicText not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



   

###################################################All Local Function#################################


#######################################Local Nav Categories######################################

def getLocalNavCategories(request):
    parentList = []
    try:
        parentLevelCategories = Category.objects.filter(parentId=None, isBrand=False, status=Category.ACTIVE).values('id','name','icon','slug')
        for parent in parentLevelCategories:
            childs =[]
            parents = {"title":parent['name'],"slug":parent['slug'], "icon":parent['icon'],"id":parent['id'], "menuComponent":"MegaMenu1","href":"/category/"+parent['slug']}
            childCategory = Category.objects.filter(parentId=parent['id'], status=Category.ACTIVE).values('id','name','slug','icon')
            if childCategory:
                for child in childCategory:
                    subChilds =[]
                    subCategory =Category.objects.filter(parentId=child['id'], status=Category.ACTIVE).values('id','name','slug','icon')
                    if subCategory:
                        for sub in subCategory:
                            subChilds.append({'title':sub['name'],"href":"/category/"+sub['slug']})
                    childs.append({"title":child['name'],"slug":parent['slug'],"href":"/category/"+child['slug'],"subCategories":subChilds})
                    
            parents['menuData'] = {"categories":childs}
            parentList.append(parents)
    except Exception as e:
        logger.error("Exception in getNavCategories: %s " %(str(e)))
    return JsonResponse(parentList, safe=False)
##############################################LoCal Product Categories#################################

def getLocalProductCategories(request):
    parentList = []
    try:
        parentLevelCategories =Category.objects.filter( parentId=None).values('id','name','icon')
        for parent in parentLevelCategories:
            childs =[]
            parents = {'label':parent['name'], 'icon':parent['icon'],'value':parent['id'], 'disabled':False}
            childCategory = Category.objects.filter(parentId=parent['id']).values('id','name','slug','icon')
            if childCategory:
                for child in childCategory:
                    childs.append({'label':child['name'],'value':child['id'], 'children':[],'disabled':False})
                    parents['disabled'] = True
            parents['children'] = childs
            parentList.append(parents)
    except Exception as e:
        logger.error("Exception in getProductCategories: %s " %(str(e)))
    return JsonResponse(parentList, safe=False)


#################GET Local Categories#########################


def getAllLocalCategories(request):
    sortedList = []
    try:
        categoryObject = list(Category.objects.filter(isBrand=False,parentId=None).values('id','slug','parentId','name','description','showAtHome','icon'))
        for cat in categoryObject:
            sortedList = sortedList + [cat]
            # print("catList: ",sortedList)
            children = list(Category.objects.filter(isBrand=False,parentId=cat['id']).values('id','slug','parentId','parentId__name','name','description','showAtHome','icon'))
            sortedList = sortedList+children
    except Exception as e:
        logger.error("Exception in getAllCategories: %s " %(str(e)))
    # print(sortedList)
    return JsonResponse(sortedList, safe=False)



#######################getAllPaginatedCategories Local Only#################

@permission_classes((IsAuthenticated,))
class getAllLocalPaginatedCategories(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    pagination_class = CustomResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_queryset(self):
        categoryObject = Category.objects.filter(isBrand=False,status=1)
        return categoryObject
    


##################################################GET LOCAL CATEGORY#####################################

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
@is_admin
@csrf_exempt
def getLocalCategory(request):
    categoryObject = {}
    slug = request.data['slug']
    try:
        categoryObject = list(Category.objects.filter(slug=slug).values('id','slug','parentId','name','description','showAtHome','icon','metaUrl','metaTitle','metaDescription','status').order_by('parentId'))
    except Exception as e:
        logger.error("Exception in getCategory: %s " %(str(e)))
    return JsonResponse(categoryObject, safe=False)



#########################Get Local Parent Category################################################

def getLocalParentCategories(request):
    categoryObject = {}
    try:
        categoryObject = list(Category.objects.filter(parentId__isnull=True).values('id','parentId','name').order_by('name'))
    except Exception as e:
        logger.error("Exception in getParentCategories: %s " %(str(e)))
    return JsonResponse(categoryObject, safe=False)



#########################Get Local Sub Category################################################



def getLocalSubCategories(request):
    categoryObject = {}
    try:
        categoryObject = list(Category.objects.filter(parentId__isnull=False).values('id','parentId','name').order_by('name'))
    except Exception as e:
        logger.error("Exception in getSubCategories: %s " %(str(e)))
    return JsonResponse(categoryObject, safe=False)







################################################ADD ITEM###################################################


@permission_classes((IsAuthenticated,))
@api_view(['GET', 'POST','PUT'])
@is_admin
@csrf_exempt
def addItemCategory(request):
    if request.method == 'POST':
        category_list = json.loads(request.POST.get('category'))
        item_id = request.GET.get('itemId')
       
        if not category_list or not item_id:
            return JsonResponse({'success': False, 'error': 'Invalid parameters'})

        for category in category_list:
            category_id = category['id']
            category_item = CategoryItem(categoryId_id=category_id, itemId_id=item_id)
            category_item.save()

        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

@permission_classes((IsAuthenticated,))
@api_view(['GET', 'POST','PUT'])
@is_admin
@csrf_exempt
def addItemGallery(request):
    if request.method == 'POST':
        item_id = request.query_params.get('itemId')
        images = request.FILES.getlist('image')

        for image in images:
            item_gallery = ItemGallery(itemId_id=item_id, image=image)
            item_gallery.save()

        return JsonResponse({'success': True, 'item_id': item_id})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})



@permission_classes((IsAuthenticated,))
@api_view(['GET', 'POST','PUT'])
@is_admin
@csrf_exempt

def addItem(request):
    if request.method == 'POST':

        image=request.POST.get('image')
        name = request.POST.get('name')
        sku = request.POST.get('sku')
        descr = request.POST.get('description')
        weight = request.POST.get('weight')
        manufacturer = request.POST.get('manufacturer')
        length = request.POST.get('length')
        height = request.POST.get('height')
        width = request.POST.get('width')
        stock = request.POST.get('stock')
        isbn = request.POST.get('isbn')
        mrp = request.POST.get('mrp')
        saleprice = request.POST.get('salePrice')
        author = request.POST.get('author')
        image = request.FILES.get('image')
        youtube_link = request.POST.get('youtube_link')
        facebook_link = request.POST.get('facebook_link')
        twitter_link = request.POST.get('twitter_link')
        instagram_link = request.POST.get('instagram_link')
        slug = request.POST.get('slug')
        metaUrl = request.POST.get('metaUrl')
        metaTitle = request.POST.get('metaTitle')
        metaDescription = request.POST.get('metaDescription')
        isNewArrival = request.POST.get('isNewArrival')
        newArrivalTill = request.POST.get('newArrivalTill')
        isFeatured = request.POST.get('isFeatured')
        extPosId=request.POST.get('extPosId')
        discount = request.POST.get('discount')

        item = Item(
            name=name,
            sku=sku,
            description =descr,
            weight=weight,
            manufacturer=manufacturer,
            length=length,
            height=height,
            width=width,
            stock=stock,
            mrp=mrp,
            salePrice=saleprice,
            author=author,
            image=image,
            youtube_link=youtube_link,
            facebook_link=facebook_link,
            twitter_link=twitter_link,
            instagram_link=instagram_link,
            slug=slug,
            isbn=isbn,
            metaUrl=metaUrl,
            metaTitle=metaTitle,
            metaDescription=metaDescription,
            isNewArrival=isNewArrival,
            newArrivalTill=newArrivalTill,
            isFeatured=isFeatured,
            extPosId=extPosId,
            discount=discount,
        )
        item.save()

        res = {
            'success': True,
           
            'item': {
                'id': item.id,
                'name': item.name,
            }
        }

        return JsonResponse(res)
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)# @api_view(['POST'])

@api_view(['GET', 'POST','PUT'])
@permission_classes((IsSuperAdmin,))

@is_admin
@csrf_exempt
def addSiteSetting(request):
    
    # site_logo = request.FILES.get('site_logo')
    site_name = request.POST.get('site_name')
    site_description = request.POST.get('site_description')
    site_metatitle = request.POST.get('site_metatitle')
    site_banner_text = request.POST.get('site_banner_text')
    # site_banner_image = request.FILES.get('site_banner_image')
    top_bar_left_phone = request.POST.get('top_bar_left_phone')
    top_bar_left_email = request.POST.get('top_bar_left_email')
    footer_description = request.POST.get('footer_description')
    footer_second_column_heading=request.POST.get('column_two_heading')
    footer_third_column_heading=request.POST.get('column_three_heading')
    footer_fourth_column_heading = request.POST.get('footer_fourth_column_heading')
    footer_fourth_column_content = request.POST.get('footer_fourth_column_content')
    facebook = request.POST.get('facebook')
    twitter = request.POST.get('twitter')
    instagram = request.POST.get('instagram')
    youtube = request.POST.get('youtube')
    app_links = request.POST.get('app_links')
    app_store = request.POST.get('app_store')
    banner_slider_image = request.FILES.get('banner_slider_image')
    shipping=request.POST.get('shipping')
    whatsapp=request.POST.get('whatsapp')
    splashtime = request.POST.get('splashtime')
    currency=request.POST.get('currency')


    name = request.POST.get('socialname')
    provider = request.POST.get('provider')
    client_id =request.POST.get('clientid')
    secret =request.POST.get('clientsecret')
    
   


    # footer_logo = request.FILES.get('footer_logo')
    top_bar_right_items = []
    column_two_links = []
    column_three_links = []

    site_settings = SiteSettings.objects.first()
    # social_app= SocialApp.objects.first()
   
    existing_site_logo = site_settings.site_logo if site_settings else None
    existing_site_splash = site_settings.site_splash if site_settings else None

    existing_footer_logo = site_settings.footer_logo if site_settings else None

    site_logo_file = request.FILES.get('site_logo')
    site_splash_file = request.FILES.get('site_splash')

    footer_logo_file = request.FILES.get('footer_logo')

    site_logo = site_logo_file if site_logo_file else existing_site_logo
    site_splash = site_splash_file if site_splash_file else existing_site_splash

    footer_logo = footer_logo_file if footer_logo_file else existing_footer_logo
    





    if site_settings:
        site_settings.site_logo = site_logo
        site_settings.site_name = site_name
        site_settings.site_description = site_description
        site_settings.site_metatitle = site_metatitle
        site_settings.site_banner_text = site_banner_text
        site_settings.shipping = shipping
        site_settings.whatsapp = whatsapp
        site_settings.top_bar_left_phone = top_bar_left_phone
        site_settings.top_bar_left_email = top_bar_left_email
        site_settings.footer_description = footer_description
        site_settings.footer_second_column_heading= footer_second_column_heading
        site_settings.footer_third_column_heading= footer_third_column_heading
        site_settings.footer_fourth_column_heading = footer_fourth_column_heading
        site_settings.footer_fourth_column_content = footer_fourth_column_content
        site_settings.facebook = facebook
        site_settings.twitter = twitter
        site_settings.instagram = instagram
        site_settings.youtube = youtube
        site_settings.app_links = app_links
        site_settings.app_store = app_store
        site_settings.site_splash=site_splash
        site_settings.splashtime=splashtime
        site_settings.currency=currency
      
        # site_settings.banner_slider_image = banner_slider_image
        site_settings.footer_logo = footer_logo
    else:
        site_settings = SiteSettings(
            site_logo=site_logo,
            site_name=site_name,
            site_description=site_description,
            site_metatitle=site_metatitle,
            site_banner_text=site_banner_text,
            shipping=shipping,
            whatsapp=whatsapp,
            splashtime=splashtime,
            # site_banner_image=site_banner_image,
            top_bar_left_phone=top_bar_left_phone,
            top_bar_left_email=top_bar_left_email,
            footer_description=footer_description,
            footer_second_column_heading= footer_second_column_heading,
            footer_third_column_heading= footer_third_column_heading,
            footer_fourth_column_heading=footer_fourth_column_heading,
            footer_fourth_column_content=footer_fourth_column_content,
            facebook=facebook,
            twitter=twitter,
            instagram=instagram,
            youtube=youtube,
            app_links=app_links,
            app_store=app_store,
            # banner_slider_image=banner_slider_image,
            footer_logo=footer_logo,
            site_splash=site_splash,
            currency=currency,
        )

    site_settings.save()
    try:
        social_app = SocialApp.objects.get(provider=provider)
        
        social_app.name = name
        social_app.client_id = client_id
        social_app.secret = secret
        social_app.save()
        
    except SocialApp.DoesNotExist:
        if client_id and secret:
            SocialApp.objects.create(
                name=name,
                provider=provider,
                client_id=client_id,
                secret=secret
            )

    for key in request.POST:
        if key.startswith('top_bar_right_items'):
            item_data = request.POST.get(key)
            try:
                item_data = json.loads(item_data)
                top_bar_right_items.append(item_data)
            except json.JSONDecodeError as e:
                print("JSON decoding error:", str(e))


    for item in top_bar_right_items:
        priority = int(item['priority']) if item['priority'] is not None else 0
        item_name = item.get('name')
        item_link = item.get('link')

        existing_item = TopBarRightItem.objects.filter(site_settings=site_settings, name=item_name).first()

        if existing_item:
            existing_item.priority = priority
            existing_item.link = item_link
            existing_item.save()
        else:
            topbar_right_item = TopBarRightItem(
                site_settings=site_settings,
                name=item_name,
                priority=priority,
                link=item_link
            )
            topbar_right_item.save()

   

    # Processing column two items
    for key in request.POST:
        if key.startswith('column_two_links'):
            item_data = request.POST.get(key)
            try:
                item_data = json.loads(item_data)
                column_two_links.append(item_data)
            except json.JSONDecodeError as e:
                print("JSON decoding error:", str(e))

    for item in column_two_links:
        priority = int(item['priority']) if item['priority'] is not None else 0
        item_name = item.get('name')
        item_link = item.get('link')

        existing_item = FooterColumnItem.objects.filter(site_settings=site_settings, name=item_name, column=2).first()

        if existing_item:
            existing_item.priority = priority
            existing_item.link = item_link
            existing_item.save()
        else:
            footer_column_item = FooterColumnItem(
                site_settings=site_settings,
                name=item_name,
                priority=priority,
                link=item_link,
                column=2  # Set the column number to 2 for column two items
            )
            footer_column_item.save()

    # Processing column three items
    for key in request.POST:
        if key.startswith('column_three_links'):
            item_data = request.POST.get(key)
            try:
                item_data = json.loads(item_data)
                column_three_links.append(item_data)
            except json.JSONDecodeError as e:
                print("JSON decoding error:", str(e))

    for item in column_three_links:
        priority = int(item['priority']) if item['priority'] is not None else 0
        item_name = item.get('name')
        item_link = item.get('link')

        existing_item = FooterColumnItem.objects.filter(site_settings=site_settings, name=item_name, column=3).first()

        if existing_item:
            existing_item.priority = priority
            existing_item.link = item_link
            existing_item.save()
        else:
            footer_column_item = FooterColumnItem(
                site_settings=site_settings,
                name=item_name,
                priority=priority,
                link=item_link,
                column=3  # Set the column number to 3 for column three items
            )
            footer_column_item.save()

    existing_slider_images = (
        SiteImage.objects.filter(site_settings=site_settings)
        if site_settings
        else SiteImage.objects.none()
    )

    


    slider_images = []

    for key in request.FILES:
        if key.startswith('banner_slider_image'):
            file_list = request.FILES.getlist(key)
            slider_images.extend(file_list)

   

    for slider_image in slider_images:
        existing_image = SiteImage.objects.filter(site_settings=site_settings, image=slider_image).first()
        if existing_image:
            existing_image.image = slider_image
            existing_image.save()
        else:
            SiteImage.objects.create(site_settings_id=site_settings.id, image=slider_image)




    return JsonResponse({"message": "Site settings created"}, status=201)

@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
# @is_admin
@csrf_exempt
def getGeneralSetting(request):
    try:
        generalObject = list(SiteSettings.objects.values())
    except Exception as e:
        logger.error("Exception in getsliderimage: %s " %(str(e)))
    return JsonResponse(generalObject, safe=False)
    
@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))

def getLocalSlider(request):
    try:
        slider_set = SiteImage.objects.order_by('-id')[:5]

        sliderObject = list(slider_set.values())
    except Exception as e:
        logger.error("Exception in getsliderimage: %s " %(str(e)))
        sliderObject = []

    return JsonResponse(sliderObject, safe=False)

@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))

def getFooterSettings(request):
    site_settings = SiteSettings.objects.first()
    
    if site_settings:
        footer_data = {
            'footer_logo': str(site_settings.footer_logo),  
            'footer_description': site_settings.footer_description,
            
            'footer_fourth_column_heading': site_settings.footer_fourth_column_heading,
            'footer_fourth_column_content': site_settings.footer_fourth_column_content,
            'column_two_heading': site_settings.footer_second_column_heading,
            'column_three_heading': site_settings.footer_third_column_heading,
            'column_two_links': [],
            'column_three_links': [],
            'facebook':str(site_settings.facebook),
            'twitter':str(site_settings.twitter),
            'instagram':str(site_settings.instagram),
            'youtube':str(site_settings.youtube),
            'app_links':str(site_settings.app_links),
            'app_store':str(site_settings.app_store),
            # 'banner_slider_image':str(site_settings.banner_slider_image)
        }

        #  column two 
        column_two_links = FooterColumnItem.objects.filter(site_settings=site_settings)
        for link in column_two_links:
            link_data = {
                'name': link.name,
                'priority': link.priority,
                'link': link.link,
                'column':link.column
            }
            footer_data['column_two_links'].append(link_data)

        #  column three 
        column_three_links = FooterColumnItem.objects.filter(site_settings=site_settings)
        for link in column_three_links:
            link_data = {
                'name': link.name,
                'priority': link.priority,
                'link': link.link,
                'column':link.column

            }
            footer_data['column_three_links'].append(link_data)

        return JsonResponse(footer_data, status=200)
    else:
        return JsonResponse({"message": "Footer settings not found"}, status=404)



# @permission_classes((IsAuthenticated,))
# # @api_view(['GET', 'POST','PUT'])
# @is_admin
# @csrf_exempt
def getStatistics(request):
    stat_type = request.GET.get('type')

    
    current_date = timezone.now()
    thirty_days_ago = current_date - timedelta(days=30)
    week_ago = current_date - timedelta(days=7)


    if stat_type == 'currentmonth':
        orders = Order.objects.filter(timestamp__year=current_date.year, timestamp__month=current_date.month)
    elif stat_type == 'last30days':
        orders = Order.objects.filter(timestamp__gte=thirty_days_ago)
    else:
        orders = Order.objects.filter(timestamp__gte=thirty_days_ago)



        #############################Current Month##########

    current_monthsale=Order.objects.filter(timestamp__year=current_date.year, timestamp__month=current_date.month,status='CONFIRMED')
    current_month_sale =current_monthsale.aggregate(total_sale=Sum('totalBill')- Sum('deliveryCharges'))['total_sale']
    current_monthorder=current_monthsale.count()

##################Monthly############################
    # monthlysale = Order.objects.filter(timestamp__gte=thirty_days_ago,status='CONFIRMED')
    # total_monthly_sale = monthlysale.aggregate(total_sale=Sum('totalBill')- Sum('deliveryCharges'))['total_sale']
    # monthly_saleitem=monthlysale.count()
    monthlysale = Order.objects.filter(timestamp__gte=thirty_days_ago, status='CONFIRMED')
    total_monthly_sale = monthlysale.aggregate(total_sale=Sum('totalBill') - Sum('deliveryCharges'))['total_sale']
    monthly_saleitem = monthlysale.aggregate(total_quantity_sold=Sum('order_description_id__itemQty'))['total_quantity_sold']
    monthly_order=monthlysale.count()

###################################Weekly#################################

    # weeklysale = Order.objects.filter(timestamp__gte=week_ago,status='CONFIRMED')
    # total_weekly_sale = weeklysale.aggregate(total_sale=Sum('totalBill')- Sum('deliveryCharges'))['total_sale']
    # weekly_saleitem=weeklysale.count()
    weeklysale = Order.objects.filter(timestamp__gte=week_ago, status='CONFIRMED')
    total_weekly_sale = weeklysale.aggregate(total_sale=Sum('totalBill') - Sum('deliveryCharges'))['total_sale']
    weekly_saleitem = weeklysale.aggregate(total_quantity_sold=Sum('order_description_id__itemQty'))['total_quantity_sold']
    weekly_saleorder=weeklysale.count()


###################################All Sale ################################
    
    # total_sale = Order.objects.filter(status='CONFIRMED').aggregate(total_sale=Sum('totalBill')- Sum('deliveryCharges'))['total_sale']
    # total_saleItem=Order.objects.filter(status='CONFIRMED').count()
    total_sale = Order.objects.filter(status='CONFIRMED').aggregate(total_sale=Sum('totalBill') - Sum('deliveryCharges'))['total_sale']
    total_saleItem = OrderDescription.objects.filter(order__status='CONFIRMED').aggregate(total_quantity_sold=Sum('itemQty'))['total_quantity_sold']


    
    total_order=Order.objects.count()
    orderSerialized = OrderSerializer(orders, many=True).data

    # existing_entry = DashboardStatistics.objects.filter(name=name, stat_type=stat_type).first()

    # if existing_entry:
    #     existing_entry.value = total_statistic
    #     existing_entry.updatetime = timezone.now()
    #     existing_entry.save()
    # else:
    #     DashboardStatistics.objects.create(name=name, value=total_statistic, stat_type=stat_type)

    stock_items = Item.objects.filter(stock=0).values('id','name','stock', 'salePrice')[:5]
    
    total_outstock=Item.objects.filter(stock=0).count()
    # most_sold_item =Order.objects.filter(order_description_id__item_type=OrderDescription.PRODUCT).values('id', 'order_description_id__itemName', 'order_description_id__salePrice').annotate(Count('order_description_id__itemSku')).order_by('-item_quantity').first()
    # most_sold_items = OrderDescription.objects.annotate(item_quantity=Sum('itemQty'),).filter(item_type=OrderDescription.PRODUCT).values('id', 'itemName', 'salePrice').distinct().annotate(Count('itemSku')).order_by('-item_quantity')[:5]
    # most_sold_items = OrderDescription.objects.filter(item_type=OrderDescription.PRODUCT, isDeleted=False).values('itemSku', 'itemName', 'salePrice') .annotate(total_quantity_sold=Sum('itemQty'), item_count=Count('id')) .order_by('-total_quantity_sold') .distinct()[:5]
    most_sold_items = OrderDescription.objects.filter(item_type=OrderDescription.PRODUCT, isDeleted=False) .filter(order__status=Order.CONFIRMED).values('itemSku', 'itemName', 'salePrice') .annotate(total_quantity_sold=Sum('itemQty'), item_count=Count('id')) .order_by('-total_quantity_sold') .distinct()[:5]
    return JsonResponse({
        "current_month_sale":current_month_sale,
        "mostsold_item": list(most_sold_items),
        "monthly_order":monthly_order,
        "current_monthorder":current_monthorder,
        "monthly_sales":total_monthly_sale,
        "monthy_saleitem":monthly_saleitem,
        "total_weekly_sale":total_weekly_sale,
        "weekly_saleitem":weekly_saleitem,
        "weekly_saleorder":weekly_saleorder,
        # "orders":orderSerialized,
        "type": stat_type,
        "total_order": total_order,
        "total_sale":total_sale,
        'total_saleItem':total_saleItem,
        "stock_items": list(stock_items) ,
        "total_outstock": total_outstock,
    })


@permission_classes((IsAuthenticated,))
@api_view(['POST'])
def addReviews(request):
    try:
        rating = request.data.get('rating')
        comment = request.data.get('comment')
        username=request.data.get('username')
        userid=request.data.get('userid')
        itemid=request.data.get('itemid')
        itemname=request.data.get('itemname')
        current_date = timezone.now()


        item_id = Item.objects.get(id=itemid)
        user_id=User.objects.get(id=userid)
        user_name=User.objects.get(name=username)

        try:
            product_review = ProductReview.objects.get(itemid=item_id, userid=user_id)
            product_review.rating = rating
            product_review.review = comment
            product_review.save()
        except ObjectDoesNotExist:
            # Create a new review
            product_review = ProductReview.objects.create(
                username=user_name,
                userid=user_id,
                itemid=item_id,
                rating=rating,
                review=comment,
                itemname=itemname,
                date=current_date
            )

        return JsonResponse({'message': 'Review detail added successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@permission_classes((AllowAny,))
def getAllReviews(request):
    try:
        
        allrequest=ProductReview.objects.values()

        items = Item.objects.filter(id__in=allrequest.values_list('itemid_id', flat=True)).values('id', 'name','image')
       
        return JsonResponse({"Reviews":list(allrequest),"items":list(items)})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
    
@permission_classes((IsSuperAdmin,))
@api_view(['GET', 'POST','PUT'])
@csrf_exempt
def addVoucher(request):

    name=request.data.get("name")
    statu=request.data.get("status")
    code=request.data.get("code")
    discount=request.data.get("discount")
    startdate=request.data.get("startdate")
    enddate=request.data.get("enddate")
    image=request.data.get("voucherimage")

   
    try:
        voucher=Voucher.objects.create(name=name,status=statu,code=code,discount=discount,startdate=startdate,enddate=enddate,image=image)

        return JsonResponse({"Msg":"Voucher Created Sucessfully"},status=200)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def getAllVouchers(request):
    try:
        voucher=Voucher.objects.values()
        vouvherlist=list(voucher)
        return JsonResponse({"Msg":"Data Sucessfully Retrieved","voucher":vouvherlist},status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@permission_classes((IsSuperAdmin,))
@api_view(['GET', 'POST','PUT'])
@csrf_exempt
def deleteVoucer(request):
    id=request.data
    try:
        deletevoucher=Voucher.objects.get(id=id)
        deletevoucher.delete()
        return JsonResponse({"Msg":"Voucher Sucessfully Deleted"},status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['GET', 'POST'])
@csrf_exempt
@permission_classes((IsSuperAdmin,))

def getVoucher(request):

    id=request.data.get('id')
    print(id)

    try:

        voucher=Voucher.objects.filter(id=id).values()
        voucherlist=list(voucher)

        return JsonResponse({"Msg":"Data Sucessfully Retrieved","voucher":voucherlist},status=200)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
@is_admin
@csrf_exempt
def updateVoucher(request):
    id=request.data.get('id')
    name=request.data.get("name")
    statu=request.data.get("status")
    code=request.data.get("code")
    discount=request.data.get("discount")
    startdate=request.data.get("startdate")
    enddate=request.data.get("enddate")
    image=request.data.get("voucherimage")

    # voucher_id = Voucher.objects.get(id=id).values("id")

    try:
        voucherdata =Voucher.objects.get(id=id)
        voucherdata.name=name
        voucherdata.id=id
        voucherdata.status=statu
        voucherdata.code=code
        voucherdata.discount=discount
        voucherdata.startdate=startdate
        voucherdata.enddate=enddate
        voucherdata.image=image
        voucherdata.save()
        return JsonResponse({"Msg":"Data Updated Sucessfully"},status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@api_view(['GET', 'POST'])
def checkVoucherValidity(request):
    coupon_code = request.data.get("couponCode")
    userid=request.data.get("userid")
    try:
        voucher = Voucher.objects.get(code=coupon_code)
        if voucher.status == 1:
            currentdate = timezone.now()
            if currentdate <= voucher.enddate:
                try:
                    checkvoucher=UserVoucher.objects.get(user=userid,vouchercode=coupon_code)
                    print(checkvoucher.isused)
                    if checkvoucher:
                        if checkvoucher.isused==False:
                            return JsonResponse({"isValid": True, "couponData": {
                                "code": voucher.code,
                                "discount": voucher.discount,
                                'id':voucher.id,
                            }})
                        else:
                            return JsonResponse({"isValid": False, "message": "Coupon Code is already used",'status':'409'},status=409)
                    else:
                        return JsonResponse({"isValid": True, "couponData": {
                                "code": voucher.code,
                                "discount": voucher.discount,
                                'id':voucher.id,
                            }})
                except:
                    return JsonResponse({"isValid": True, "couponData": {
                                "code": voucher.code,
                                "discount": voucher.discount,
                                'id':voucher.id,
                            }})
            
            else:
                return JsonResponse({"isValid": False, "message": "Coupon code is expired"})
        else:
            return JsonResponse({"isValid": False, "message": "Coupon code is inactive"})
    except Voucher.DoesNotExist:
        return JsonResponse({"isValid": False, "message": "Coupon code not found"})

@api_view(['GET', 'POST'])
def saveVoucherData(request):

    userid=request.data.get("userid")
    voucherid=request.data.get("voucherid")
    vouchercode=request.data.get("vouchercode")

    user=User.objects.get(id=userid)
    voucher=Voucher.objects.get(id=voucherid)

    try:

        newdata=UserVoucher.objects.create(user=user,voucher=voucher,vouchercode=vouchercode,isused=True)
        return JsonResponse({"Msg":"Data Sucessfully Added"})
    
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)




@api_view(['POST'])
@permission_classes((IsSuperAdmin,))
@csrf_exempt
def addCountry(request):
        result = {}
       
        name=request.data['name']
        type=request.data['type']
        status=request.data['status']
        try:
            if(Country.objects.filter(name=name).exists()):
                result = {"ErrorCode": error_codes.ERROR, "ErrorMsg": error_codes.COUNTRY_ALREADY_EXIST+' - '+str(name)}
            else:
                Country.objects.create(name=name, type=type, status=status)
                result = {"ErrorCode": error_codes.SUCCESS, "ErrorMsg": error_codes.SUCCESS_MSG}
        except Exception as e:
            traceback.print_exc()
            print("Exception in addCountry ", str(e))
            result = {"ErrorCode": error_codes.ERROR, "ErrorMsg": str(e)}
            logger.error("Exception: %s" %(str(e)))
        return JsonResponse(result, safe=False)


@api_view(['POST'])
@permission_classes((IsSuperAdmin,))
@csrf_exempt
def addCity(request):
        result = {}
        # print(request.data)
        # id=request.data['id']
        name=request.data['name']
        country=request.data['country']
        type=request.data['type']
        status=request.data['status']
        countryinstance=Country.objects.get(id=country)
        try:
            if(City.objects.filter(name=name).exists()):
                result = {"ErrorCode": error_codes.ERROR, "ErrorMsg": error_codes.CITY_ALREADY_EXIST+' - '+str(name)}
            else:
                City.objects.create(name=name,country=countryinstance, type=type, status=status)
                result = {"ErrorCode": error_codes.SUCCESS, "ErrorMsg": error_codes.SUCCESS_MSG}
        except Exception as e:
            traceback.print_exc()
            print("Exception in addCity ", str(e))
            result = {"ErrorCode": error_codes.ERROR, "ErrorMsg": str(e)}
            logger.error("Exception: %s" %(str(e)))
        return JsonResponse(result, safe=False)


@api_view(['GET', 'POST'])
@permission_classes((IsSuperAdmin,))
@csrf_exempt
def getCityConfiguration(request):
    ConfigurationObject = {}
    # print(request.data)
    id = request.data['id']
    try:
        ConfigurationObject = list(City.objects.filter(id=id).values())
    except Exception as e:
        logger.error("Exception in getCityConfiguration: %s " %(str(e)))
    return JsonResponse(ConfigurationObject, safe=False)

@api_view(['GET', 'POST'])
@permission_classes((IsSuperAdmin,))
@csrf_exempt
def getCountryConfiguration(request):
    ConfigurationObject = {}
    # print(request.data)
    id = request.data['id']
    try:
        ConfigurationObject = list(Country.objects.filter(id=id).values())
    except Exception as e:
        logger.error("Exception in getCountryConfiguration: %s " %(str(e)))
    return JsonResponse(ConfigurationObject, safe=False)

@permission_classes((IsAuthenticated,))
# @method_decorator(is_admin, name='dispatch')
class getAllCountry(generics.ListCreateAPIView):
    serializer_class = CountrySerializer
    pagination_class = CustomResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name','type']

    def get_queryset(self):
        countryObject={}
        try:
            countryObject = Country.objects.filter().order_by('status')
        except Exception as e:
            logger.error("Exception in getAllCountry: %s " %(str(e)))
        return countryObject
    


@api_view(['GET', 'POST'])
@permission_classes((IsSuperAdmin,))
@csrf_exempt
def deleteCountry(request):
        context = {}
        countryId = request.data
        logger.info("Request %s " %(str(request.data)))
        try:
            countryObject = Country.objects.get(id=countryId)
            if(City.objects.filter(country=countryObject).exists()):
                result = {"ErrorCode": error_codes.ERROR, "ErrorMsg": error_codes.COUNTRY_EXST_IN_USR_SHIP_ERR_MSG}
            
            else:
                Country.objects.filter(id = countryId).delete()
                result = {"ErrorCode": error_codes.SUCCESS, "ErrorMsg": error_codes.DELETE_MSG}
            context.update(result)
            # logger.info("%s " %(str(result)))
        except Exception as e:
            result = {"ErrorCode": error_codes.ERROR, "ErrorMsg": error_codes.NOT_DELETE_MSG+' - '+str(e)}
            context.update(result)
            # print("Exception in Delete Bundle View ", str(e))
            logger.error("Exception in deleteCity: %s " %(str(e)))
            # traceback.print_exc()
        return JsonResponse(context, safe=False)




class updateCountryConfiguration(generics.UpdateAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (IsSuperAdmin,)


class getAllCity(generics.ListCreateAPIView):
    serializer_class = CitySerializer
    pagination_class = CustomResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name','type']

    def get_queryset(self):
        cityObject={}
       
        try:
            cityObject = City.objects.filter().order_by('status')
        except Exception as e:
            logger.error("Exception in getAllCity: %s " %(str(e)))
        return cityObject
    
    

class updateCityConfiguration(generics.UpdateAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (IsSuperAdmin,)



def getallcountries(request):

    try:
        countries=Country.objects.values()
        countrylist=list(countries)

        return JsonResponse({"Msg":"Data Sucessfuly retrieved","countrylist":countrylist},status=200)
    
    except Exception as e:
            logger.error("Exception in getAllCountry: %s " %(str(e)))


@api_view(['GET', 'POST'])
@permission_classes((IsSuperAdmin,))
@csrf_exempt
def deleteCity(request):
        context = {}
        cityId = request.data
        logger.info("Request %s " %(str(request.data)))
        try:
            cityObject = City.objects.get(id=cityId)
            if(UserShippingDetail.objects.filter(city=cityObject).exists()):
                result = {"ErrorCode": error_codes.ERROR, "ErrorMsg": error_codes.CITY_EXST_IN_USR_SHIP_ERR_MSG}
            elif(Order.objects.filter(custCity=cityObject).exists()):
                result = {"ErrorCode": error_codes.ERROR, "ErrorMsg": error_codes.CITY_EXST_IN_ORDER_ERR_MSG}
            else:
                City.objects.filter(id = cityId).delete()
                result = {"ErrorCode": error_codes.SUCCESS, "ErrorMsg": error_codes.DELETE_MSG}
            context.update(result)
            # logger.info("%s " %(str(result)))
        except Exception as e:
            result = {"ErrorCode": error_codes.ERROR, "ErrorMsg": error_codes.NOT_DELETE_MSG+' - '+str(e)}
            context.update(result)
            # print("Exception in Delete Bundle View ", str(e))
            logger.error("Exception in deleteCity: %s " %(str(e)))
            # traceback.print_exc()
        return JsonResponse(context, safe=False)

def getWebsiteCountries(request):

    try:
        countries=Country.objects.filter(status='ACTIVE').values()
        countrylist=list(countries)

        return JsonResponse({"Msg":"Data Sucessfuly retrieved","countrylist":countrylist},status=200)
    
    except Exception as e:
            logger.error("Exception in getAllCountry: %s " %(str(e)))



@api_view(['GET','POST'])
@permission_classes((AllowAny,))
def getWebsiteCities(request):

    country=request.query_params.get('country')
    countryinstance=Country.objects.get(name=country)

    try:
        cities=City.objects.filter(country=countryinstance).filter(status='ACTIVE').values()
        citylist=list(cities)

        return JsonResponse({"Msg":"Data Sucessfuly retrieved","citylist":citylist},status=200)
    
    except Exception as e:
            logger.error("Exception in getAllCountry: %s " %(str(e)))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addCustomerShipping(request):
    try:
        country=request.data.get('country')
        address = request.data.get('address')
        city = request.data.get('city')
        user = request.user

        if not address or not city:
            return JsonResponse({'error': 'Address and city are required'}, status=400)
        
        city_name = City.objects.get(name=city)
        country_name=Country.objects.get(name=country)

        user_shipping_detail = UserShippingDetail.objects.create(
            address=address,
            city=city_name,
            country=country_name,
            area=city+ '   '+ country,  
            user=user
        )

        return JsonResponse({'message': 'Shipping detail added successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
def updatePayment(request):
    orderno = request.data.get('orderno')
    paymentid = request.data.get('paymentid')
    paymentstatus = request.data.get('paymentstatus')
    invoice = request.data.get('invoice')

    try:
        order = Order.objects.get(orderNo=orderno)

        order.paymentid  = paymentid
        order.paymentstatus = paymentstatus
        order.customeronlinepaymentinvoice = invoice
        order.paymentsessionid=paymentid
        order.paymentMethod='Online'
        order.paymenttime=str(currentDateTime.now())
        order.save()

      

        return JsonResponse({"Msg": "Data successfully updated"})
    except Order.DoesNotExist:
        return JsonResponse({"Msg": "Order not found"}, status=404)
    except Exception as e:
        return JsonResponse({"Msg": str(e)}, status=500)

    

@api_view(['GET', 'POST'])
@permission_classes((IsSuperAdmin,))
@csrf_exempt
def addCourier(request):
    name=request.data.get('name')
    country=request.data.get('country')
    time=request.data.get('time')
    countryinstance=Country.objects.get(name=country)
    try:
        courier=Courier.objects.filter(name=name,country=countryinstance).first()
        if courier:
            return JsonResponse({"Msg": "Courier in country is already added",'status':'500'},status=500)
        else:
            newcourier=Courier.objects.create(name=name,country=countryinstance,time=time,countryname=country)
            return JsonResponse({"Msg": "Courier Sucessfully Created"},status=200)
    
    except Exception as e:
        return JsonResponse({"Msg": str(e)}, status=500)


@api_view(['GET', 'POST'])
@permission_classes((IsSuperAdmin,))
@csrf_exempt
def getCourier(request):
    
    try:
        courier=Courier.objects.values()
        courierlist=list(courier)
        return JsonResponse({"Msg": "Courier Sucessfully retrieved",'courierlist':courierlist},status=200)

    
    except Exception as e:
        return JsonResponse({"Msg": str(e)}, status=500)



@permission_classes((IsSuperAdmin,))
@api_view(['GET', 'POST','PUT'])
@csrf_exempt
def deleteCourier(request):
    id=request.data
    try:
        deletecourier=Courier.objects.get(id=id)
        deletecourier.delete()
        return JsonResponse({"Msg":"Courier Sucessfully Deleted"},status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
@api_view(['GET', 'POST'])
@csrf_exempt
@permission_classes((IsSuperAdmin,))

def getIDCourier(request):

    id=request.data.get('id')
    print(id)

    try:

        courier=Courier.objects.filter(id=id).values()
        courierlist=list(courier)

        return JsonResponse({"Msg":"Data Sucessfully Retrieved","courier":courierlist},status=200)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['GET', 'POST'])
@csrf_exempt
@permission_classes((IsSuperAdmin,))
def updateCourier(request):

    id=request.data.get('id')
    name=request.data.get('name')
    country=request.data.get('country')
    time=request.data.get('time')
    countryinstance=Country.objects.get(name=country)

    courier=Courier.objects.get(id=id)

    

    courier.name=name
    courier.country=countryinstance
    courier.time=time
    courier.countryname=country
    courier.save()

    return JsonResponse({"Msg":"Sucessfully Updated"})

@permission_classes((IsAuthenticated,))
# @method_decorator(is_admin, name='dispatch')
class getAllCourier(generics.ListCreateAPIView):
    serializer_class = CourierSerializer
    pagination_class = CustomResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_queryset(self):
        courierObject={}
        try:
            courierObject = Courier.objects.filter()
        except Exception as e:
            logger.error("Exception in getAllCourier: %s " %(str(e)))
        return courierObject

@permission_classes((IsAuthenticated,))
class getAllCourierConfiguration(generics.ListCreateAPIView):
    serializer_class = CourierConfigurationSerializerDepth
    pagination_class = CustomResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['courier','cityType','weight','status']

    def get_queryset(self):
        schoolObject={}
        try:
            schoolObject = CourierConfiguration.objects.filter().order_by('status')
        except Exception as e:
            logger.error("Exception in getAllCourierConfiguration: %s " %(str(e)))
        return schoolObject
@api_view(['POST'])
@permission_classes((IsSuperAdmin,))
@csrf_exempt
def addChargesConfiguration(request):
        result = {}
        # print(request.data)
        courier=request.data['courier']
        cityType=request.data['cityType']
        weight=request.data['weight']
        price=request.data['price']
        addOn=request.data['addOn']
        addOn= True if addOn=='true' else False
        status=request.data['status']
        try:
            if(CourierConfiguration.objects.filter(cityType=cityType,courier=courier,weight=weight).exists()):
                result = {"ErrorCode": error_codes.ERROR, "ErrorMsg": "Configuration already exists with same Courier and Weight!"}
            else:
                CourierConfiguration.objects.create(cityType=cityType, weight=weight, price=price, addOn=addOn, courier_id=courier,couriername=courier)
                result = {"ErrorCode": error_codes.SUCCESS, "ErrorMsg": error_codes.SUCCESS_MSG}
        except Exception as e:
            traceback.print_exc()
            print("Exception in addChargesConfiguration ", str(e))
            result = {"ErrorCode": error_codes.ERROR, "ErrorMsg": str(e)}
            logger.error("Exception: %s" %(str(e)))
        return JsonResponse(result, safe=False)


@api_view(['GET', 'POST'])
@permission_classes((IsSuperAdmin,))
@csrf_exempt
def getChargesConfiguration(request):
    ConfigurationObject = {}
    # print(request.data)
    id = request.data['id']
    try:
        ConfigurationObject = list(CourierConfiguration.objects.filter(id=id).values())
    except Exception as e:
        logger.error("Exception in getChargesConfiguration: %s " %(str(e)))
    return JsonResponse(ConfigurationObject, safe=False)

class updateChargesConfiguration(generics.UpdateAPIView):
    queryset = CourierConfiguration.objects.all()
    serializer_class = CourierConfigurationSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (IsSuperAdmin,)


@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def calculateWeight(request):

    cart= request.data['cartList']
    print(cart)
    city=request.data.get("city")
    addOnFlag = True
    totalWeight = 0
    shippingCharges = 0
    context = {}

    cityType=City.objects.get(name=city)


    for item in cart:
        slug = item["slug"]
        qty = item["qty"]

        try:
            product = Item.objects.get(slug=slug)
            totalWeight += float(product.weight) * float(qty)
        except Item.DoesNotExist:
            pass

    totalWeight = totalWeight/1000

    try:
        courierObj = CourierConfiguration.objects.filter(cityType=cityType.type, addOn=False).values('id','cityType','weight','price','addOn','status').order_by('weight')
        for charges in courierObj:
            if(charges['weight']>totalWeight):
                shippingCharges = charges['price']
                addOnFlag = False
                break


        if addOnFlag:
            generalPrice = CourierConfiguration.objects.get(cityType=cityType.type, weight=1)
            shippingCharges += generalPrice.price
            remainingWeight = totalWeight - 1
            remainingWeight = math.ceil(remainingWeight)
            addOnPrice = CourierConfiguration.objects.get(cityType=cityType.type, addOn=True)
            shippingCharges += addOnPrice.price*remainingWeight
        result = {"ErrorCode": error_codes.SUCCESS, "ErrorMsg": error_codes.UPDATE_MSG, "shippingCharges":shippingCharges, "totalWeight":totalWeight}
        context.update(result)
    except Exception as e:
            result = {"ErrorCode": error_codes.ERROR, "ErrorMsg": error_codes.NOT_SENT_TO_POS_MSG}
            context.update(result)
            logger.error("Exception in getShippingChargesAgainstCity: %s " %(str(e)))
            print(e)
    return JsonResponse(context, safe=False)




def cancelUnpaidOrder():
    try:
        thirty_minutes_ago = timezone.now() - timedelta(minutes=30)

        orders_to_cancel = Order.objects.filter(
            (Q(paymentstatus='unpaid') | Q(paymentstatus__isnull=True)) &
            Q(timestamp__gte=thirty_minutes_ago)
        )

        orders_to_cancel.update(status=Order.CANCELLED)

        return JsonResponse({"success": True, "message": "Orders successfully cancelled"})
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Error: {str(e)}"}, status=500)
    