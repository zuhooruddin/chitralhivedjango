
from ctypes import addressof
from email.policy import default
from pyexpat import model
from sqlite3 import Timestamp
from statistics import mode
# from turtle import pos
from unicodedata import category
from unittest.util import _MAX_LENGTH
from django.db import models
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, UserManager, AbstractUser, PermissionsMixin
from django.db import IntegrityError
from django.contrib.auth.hashers import make_password
from simple_history.models import HistoricalRecords


################### AUTH USER ##########################################



class CustomHistoricalRecords(HistoricalRecords):
    def post_save(self, instance, created, using, **kwargs):
        if not created:
            super().post_save(instance, created, using, **kwargs)

class User(AbstractBaseUser,PermissionsMixin):
    ACTIVE    = 1
    PENDING   = 2
    INACTIVE  = 3
    DELETED   = 4
    status_choice = ((ACTIVE, "ACTIVE"), (PENDING, "PENDING"), (INACTIVE, "INACTIVE"), (DELETED, "DELETED"))

    MALE    = 1
    FEMALE  = 2
    OTHER   = 3
    gender_choice = ((MALE, "MALE"), (FEMALE, "FEMALE"), (OTHER, "OTHER"))

    SUPER_ADMIN  = 1
    ADMIN        = 2
    CUSTOMER      = 3
    role_choice = ((SUPER_ADMIN, "SUPER_ADMIN"), (ADMIN, "ADMIN"), (CUSTOMER, "CUSTOMER"))

    id               = models.BigAutoField(primary_key=True)
    extPosId         = models.IntegerField(null=True)
    name             = models.CharField(max_length=100, null=True)
    password         = models.CharField(max_length=255, null=True)
    email            = models.CharField(max_length=100, unique=True, null=True)
    username         = models.CharField(max_length=100, unique=True, null=True)
    phone            = models.CharField(max_length=100, null=True)
    mobile           = models.CharField(max_length=100, null=True)
    gender           = models.IntegerField(null=True, choices=gender_choice)
    profile_pic      = models.ImageField(upload_to='users_profile_pics/', default='users_profile_pics/default-user-icon.jpg', null=True)
    address          = models.CharField(max_length=250, null=True)
    membership       = models.IntegerField(null=True)
    points           = models.IntegerField(null=True)
    role             = models.IntegerField(null=False, choices=role_choice, default=CUSTOMER)
    status           = models.IntegerField(null=False, choices=status_choice, default=ACTIVE)
    totp_key         = models.CharField(max_length=128, null=True)
    is_first_login   = models.BooleanField(null=False, default=True) 
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    history = CustomHistoricalRecords()
    objects = UserManager()
    USERNAME_FIELD = 'username'
    class Meta:
        db_table = "auth_user"

    def __str__(self):
        return self.name or self.username or self.email or str(self.id)
    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs) 
       
    
    def AddUser(mapping):
        obj = User()
        try:
            for (field, value) in (mapping.items()):
                if value:
                    if field=='password':
                        setattr(obj,field,make_password(value))
                    else:
                        setattr(obj, field,value)
            responseObject = obj.save()
            print('Models')
            print(responseObject)
            # return obj
        except IntegrityError:
            # print("Exception in AddCategory(model): " + str(e))
            raise
        return responseObject
    
    
class Country(models.Model):
    ACTIVE    = 'ACTIVE'
    INACTIVE  = 'INACTIVE'
    DELETED   = 'DELETED'
    status_choice = ((ACTIVE, "ACTIVE"), (INACTIVE, "INACTIVE"), (DELETED, "DELETED"))
    SAME    = 'SAME'
    MAJOR   = 'MAJOR'
    OTHER   = 'OTHER'
    type_choices = ((SAME, 'SAME'),(MAJOR, 'MAJOR'),(OTHER, 'OTHER'),)

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=300)
    status = models.CharField(max_length=100, choices=status_choice, default=ACTIVE)
    type = models.CharField(max_length=100, choices=type_choices, default=OTHER)
    class Meta:
        db_table = "country"
    
class City(models.Model):
    ACTIVE    = 'ACTIVE'
    INACTIVE  = 'INACTIVE'
    DELETED   = 'DELETED'
    status_choice = ((ACTIVE, "ACTIVE"), (INACTIVE, "INACTIVE"), (DELETED, "DELETED"))
    SAME    = 'SAME'
    MAJOR   = 'MAJOR'
    OTHER   = 'OTHER'
    type_choices = ((SAME, 'SAME'),(MAJOR, 'MAJOR'),(OTHER, 'OTHER'),)

    id = models.BigAutoField(primary_key=True)
    country=models.ForeignKey(Country,null=True,on_delete=models.CASCADE)
    api_id = models.IntegerField(unique=True,null=True)
    name = models.CharField(max_length=300)
    status = models.CharField(max_length=100, choices=status_choice, default=ACTIVE)
    type = models.CharField(max_length=100, choices=type_choices, default=OTHER)
    class Meta:
        db_table = "city"

class UserShippingDetail(models.Model):
    
    id              = models.BigAutoField(primary_key=True)
    house           = models.CharField(max_length=100, null=True)
    country=models.CharField(max_length=100,null=True)
    street          = models.CharField(max_length=100,null=True)
    area            = models.CharField(max_length=100, null=True)
    address          = models.CharField(max_length=500, null=True)
    city            = models.CharField(max_length=100, null=True)
    zip             = models.CharField(max_length=20, null=True)
    user            = models.ForeignKey(User, on_delete=models.PROTECT, related_name='user_personal_details', null=True)
    class Meta:
        db_table = "user_shipping_detail"
    
    

#################### CATEGORY MODEL ######################################

class Category(models.Model):
    
    ACTIVE    = 1
    INACTIVE  = 2
    DELETED   = 3
    status_choice = ((ACTIVE, "ACTIVE"), (INACTIVE, "INACTIVE"),(DELETED, "DELETED"))

    INTERNAL    = 1
    EXTERNAL    = 2
    MIX         = 3
    pos_choice = ((EXTERNAL, "EXTERNAL"), (INTERNAL, "INTERNAL"),(MIX, "MIX"))


    id                          = models.BigAutoField(primary_key=True)
    extPosId                    = models.IntegerField(null=True, default=0)
    extPosParentId              = models.IntegerField(null=True)
    parentId                    = models.ForeignKey("self", on_delete=models.PROTECT, null=True, blank=True)
    name                        = models.CharField(max_length=100, null=False)
    slug                        = models.CharField(max_length=200, null=False, unique=True)
    description                 = models.CharField(null=True,max_length=1000 )
    icon                        = models.ImageField(upload_to='category_icon/', default='category_icon/default-category-icon.jpg', null=True)
    showAtHome                  = models.IntegerField(null=False, default=0)
    appliesOnline               = models.IntegerField(null=False, default=0)
    syncTs                      = models.IntegerField(null=True)
    lovSequence                 = models.IntegerField(null=True)
    metaUrl                     = models.CharField(max_length=150, null=True)
    metaTitle                   = models.CharField(max_length=100, null=True)
    metaDescription             = models.CharField(max_length=500, null=True)
    isBrand                    = models.BooleanField(default=False)
    catName                     = models.CharField(max_length=100, null=True)
    priority                    = models.IntegerField(null=True)
    posType                     = models.IntegerField(null=False, choices=pos_choice, default=INTERNAL)
    status                      = models.IntegerField(null=False, choices=status_choice, default=ACTIVE)
    history = CustomHistoricalRecords()

    class Meta:
        db_table = "categories"
    
    # def AddCategory1(categoryExtPosId, parentId, name, categoryDescription, appliesOnline, syncTs, lovSequence, catStatus,posStatus):
    #     try:
    #         categoryObj = Category.objects.create(categoryExtPosId=categoryExtPosId, parentId=parentId, name=name, categoryDescription=categoryDescription, appliesOnline=appliesOnline, syncTs=syncTs, lovSequence=lovSequence, catStatus=catStatus,posStatus=posStatus)
    #     except Exception as e:
    #         print("Exception in AddCategory(model): " + str(e))
    #     return categoryObj
    
    # def AddLocalCategory( parentId, name, categoryDescription, appliesOnline,catStatus):
    #     try:
    #         categoryObj = Category.objects.create( parentId=parentId, name=name, categoryDescription=categoryDescription, catStatus=catStatus)
    #     except Exception as e:
    #         print("Exception in AddCategory(model): " + str(e))
    #     return categoryObj

    # used in synchronization 
    def AddCategory(mapping):
        obj = Category()
        try:
            for (field, value) in (mapping.items()):
                setattr(obj, field,value)
            obj.save()
        except IntegrityError:
            # print("Exception in AddCategory(model): " + str(e))
            raise
        return obj

    # used in synchronization
    def UpdateCategory(mapping,extPos):
        obj = Category.objects.get(extPosId=extPos)
        try:
            for (field, value) in (mapping.items()):
                setattr(obj, field,value)
            obj.save()
        except IntegrityError:
            # print("Exception in AddCategory(model): " + str(e))
            raise
        return obj

    def UpdateCategory1(categoryExtPosId, parentId, name, categoryDescription, appliesOnline, syncTs, lovSequence, catStatus):
        result = None
        try:
            categoryObj = Category.objects.get(categoryExtPosId=categoryExtPosId)
            categoryObj.parentId=parentId 
            categoryObj.name=name 
            categoryObj.description=categoryDescription 
            categoryObj.appliesOnline=appliesOnline
            categoryObj.syncTs=syncTs
            categoryObj.lovSequence=lovSequence
            categoryObj.status=catStatus
            categoryObj.save()
            result = categoryObj 
        except Exception as e:
            print("Exception in UpdateCategory(model): " + str(e))
        return result

###############################  ITEM MODELS ################################

class Item(models.Model):
    ACTIVE    = 1
    INACTIVE  = 2
    DELETED   = 3
    status_choice = ((ACTIVE, "ACTIVE"), (INACTIVE, "INACTIVE"), (DELETED, "DELETED"))

    id                          = models.BigAutoField(primary_key=True)
    extPosId                    = models.IntegerField(null=False)
    name                        = models.CharField(max_length=150, null=False)
    slug                        = models.CharField(max_length=150, unique=True)
    sku                         = models.CharField(max_length=100, unique=True,null=False)
    image                       = models.ImageField(upload_to='item_image', default='idris/asset/default-item-image.jpg', null=True)
    description                 = models.CharField(max_length=2000, null=True)
    appliesOnline               = models.IntegerField(null=False, default=0)
    weightGrams                 = models.CharField(max_length=150, null=True)
    manufacturer                = models.CharField(max_length=150, null=True)
    # author                      = models.CharField(max_length=50, null=True)
    length                      = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    # breadth                     = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    height                      = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    weight                      = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    width                       = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    stock                       = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    stockCheckQty               = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    mrp                         = models.IntegerField(null=True)
    salePrice                   = models.IntegerField(null=True)
    discount                    = models.IntegerField(default=0)
    extTimestamp                = models.DateTimeField(null=True)
    # timestamp                   = models.DateTimeField(max_length=100, null=True)
    author                      = models.CharField(max_length=100, null=True)
    isbn                        = models.CharField(max_length=100, null=True)
    aliasCode                   = models.CharField(max_length=100, null=True)
    descriptionLink             = models.CharField(max_length=200, null=True)
    youtube_link                = models.CharField(max_length=200,null=True)
    facebook_link               = models.CharField(max_length=200,null=True)
    twitter_link                = models.CharField(max_length=200,null=True)
    instagram_link              = models.CharField(max_length=200,null=True)
    itemInstructions            = models.CharField(max_length=500, null=True)
    itemTag                     = models.CharField(max_length=200, null=True)
    vendorTag                   = models.CharField(max_length=200, null=True)
    isNewArrival                = models.IntegerField(null=False,default=0)
    newArrivalTill              = models.DateTimeField(null=True)
    metaUrl                     = models.CharField(max_length=150, null=True)
    metaTitle                   = models.CharField(max_length=150, null=True)
    metaDescription             = models.CharField(max_length=500, null=True)
    timestamp                   = models.DateTimeField(default=timezone.now, null=True)
    # updatedAt                   = models.DateTimeField(default=timezone.now, null=True)
    status                      = models.IntegerField(null=False, choices=status_choice, default=ACTIVE)
    isFeatured                  = models.IntegerField(null=False,default=0)
    history = CustomHistoricalRecords()

    class Meta:
        db_table = "item"
    
    def AddItem(mapping):
        obj = Item()
        try:
            for (field, value) in (mapping.items()):
                setattr(obj, field,value)
            obj.save()
        except IntegrityError:
            # print("Exception in AddCategory(model): " + str(e))
            raise

        return obj
    
    def UpdateItem(mapping,extPosId):
        obj = Item.objects.get(extPosId=extPosId)
        try:
            for (field, value) in (mapping.items()):
                setattr(obj, field,value)
            obj.save()
        except IntegrityError:
            # print("Exception in AddCategory(model): " + str(e))
            raise

        return obj

class ItemGallery(models.Model):
    ACTIVE      = 1
    INACTIVE    = 2
    DELETED     = 3
    status_choice = ((ACTIVE, "ACTIVE"), (INACTIVE, "INACTIVE"), (DELETED, "DELETED"))

    id                  = models.BigAutoField(primary_key=True)
    itemId              = models.ForeignKey(Item,on_delete=models.PROTECT, null=True, blank=True)
    image               = models.ImageField(upload_to='item_images/', default='item_images/default-item-image.jpg', null=True)
    # timeStamp             = models.DateTimeField(default=timezone.now, null=True)
    status              = models.IntegerField(null=False, choices=status_choice, default=ACTIVE)
    history = CustomHistoricalRecords()

    class Meta:
        db_table = "item_gallery"

class ItemTags(models.Model):
    ACTIVE      = 1
    INACTIVE    = 2
    DELETED     = 3
    status_choice = ((ACTIVE, "ACTIVE"), (INACTIVE, "INACTIVE"), (DELETED, "DELETED"))

    id                  = models.BigAutoField(primary_key=True)
    itemId              = models.ForeignKey(Item,on_delete=models.PROTECT, null=True, blank=True)
    name                = models.ImageField(upload_to='item_images/', default='item_images/default-item-image.jpg', null=True)
    # timeStamp             = models.DateTimeField(default=timezone.now, null=True)
    status              = models.IntegerField(null=False, choices=status_choice, default=ACTIVE)
    history = CustomHistoricalRecords()

    class Meta:
        db_table = "item_tag"

# class ItemSeo(models.Model):
#     ACTIVE          = 1
#     INACTIVE        = 2
#     DELETED         = 3
#     status_choice   = ((ACTIVE, "ACTIVE"), (INACTIVE, "INACTIVE"), (DELETED, "DELETED"))

#     id                  = models.BigAutoField(primary_key=True)
#     itemId              = models.IntegerField(null=False, default=0)
#     metaUrl             = models.CharField(max_length=150, null=True)
#     metaTitle           = models.CharField(max_length=150, null=True)
#     metaDescription     = models.CharField(max_length=150, null=True)
#     # timeStamp          = models.DateTimeField(default=timezone.now, null=True)
#     status              = models.IntegerField(null=False, choices=status_choice, default=ACTIVE)

#     class Meta:
#         db_table = "item_seo"



############################### CATEGORY & ITEM BRIDGE TABLE #############################
class CategoryItem(models.Model):
    ACTIVE      = 1
    INACTIVE    = 2
    DELETED     = 3
    status_choice = ((ACTIVE, "ACTIVE"), (INACTIVE, "INACTIVE"), (DELETED, "DELETED"))

    id                          = models.BigAutoField(primary_key=True)
    categoryId                  = models.ForeignKey(Category, on_delete=models.PROTECT,related_name='cat_item_categoryid', null=True)
    itemId                      = models.ForeignKey(Item, on_delete=models.PROTECT,related_name='cat_item_itemid', null=True)
    level                       = models.IntegerField(null=True, blank=True)
    # timeStamp                   = models.DateTimeField(default=timezone.now, null=True)
    status                      = models.IntegerField(null=False, choices=status_choice, default=ACTIVE)

    class Meta:
        db_table = "category_item"


############### Category & Item Sync Track Progress Model #################

class TaskProgress(models.Model):
    CATEGORY    = "CATEGORY_SYNC"
    ITEM        = "ITEM_SYNC"
    sync_type_choice = ((CATEGORY, "CATEGORY_SYNC"), (ITEM, "ITEM_SYNC"))

    id              = models.BigAutoField(primary_key=True)
    taskId          = models.CharField(max_length=50,null=True)
    progress        = models.IntegerField(null=True)
    total           = models.IntegerField(null=True)
    user            = models.ForeignKey(User, on_delete=models.PROTECT,related_name='task_user', null=True)
    uploadTime      = models.DateTimeField(auto_now_add=True)
    completionTime  = models.DateTimeField(null=True)
    syncType        = models.CharField(null=False,max_length=25, choices=sync_type_choice)
    status          = models.CharField(max_length=25,default='',null=False)
    statusReason    = models.CharField(max_length=555,default='',null=True)
    cancelTask      = models.BooleanField(default=False)

    class Meta:
        db_table = "task_progress"

def task_canceled():
    return TaskProgress.objects.filter(syncType="ITEM_SYNC",cancelTask=True,status="CANCELLED").exists()
def task_stopped():
    TaskProgress.objects.filter(syncType="ITEM_SYNC",cancelTask=True,status="CANCELLED").update(status="STOPPED")
    return True




############### Bundle Model #################

class Bundle(models.Model):
    ACTIVE      = 1
    INACTIVE    = 2
    DELETED     = 3
    status_choice = ((ACTIVE, "ACTIVE"), (INACTIVE, "INACTIVE"), (DELETED, "DELETED"))

    BRAND      = "BRAND"
    PRODUCT     = "PRODUCT"
    bundle_type = ((BRAND, "BRAND"), (PRODUCT, "PRODUCT"))


    id                  = models.BigAutoField(primary_key=True)
    name                = models.CharField(null=False, blank=False, max_length=100)
    slug                = models.CharField(null=True, blank=True, max_length=150, unique=True)
    sku                 = models.CharField(null=True, blank=True, max_length=150, unique=True)
    image               = models.ImageField(upload_to='bundle_images/', default='bundle_images/default-bundle.png', null=True)
    mrp               = models.IntegerField(null=True, blank=True)
    salePrice           = models.IntegerField(null=True, blank=True)
    description         = models.CharField(max_length=1000, null=True)
    showAtHome          = models.IntegerField(null=False, default=0)
    metaUrl             = models.CharField(max_length=150, null=True)
    metaTitle           = models.CharField(max_length=150, null=True)
    metaDescription     = models.CharField(max_length=150, null=True)
    # timeStamp             = models.DateTimeField(default=timezone.now, null=True)
    bundleType          = models.CharField(max_length=100,null=False, choices=bundle_type)
    categoryId          = models.ForeignKey(Category, on_delete=models.PROTECT,related_name='bundle_category', null=True)
    priority            = models.IntegerField(null=True)
    status              = models.IntegerField(null=False, choices=status_choice, default=ACTIVE)
    history = CustomHistoricalRecords()

    class Meta:
        db_table = "bundle"

class BundleItem(models.Model):
    ACTIVE      = 1
    INACTIVE    = 2
    DELETED     = 3
    status_choice = ((ACTIVE, "ACTIVE"), (INACTIVE, "INACTIVE"), (DELETED, "DELETED"))

    id                  = models.BigAutoField(primary_key=True)
    bundleId            = models.ForeignKey(Bundle, on_delete=models.PROTECT,related_name='bundle_id_bundleItems', null=True)
    itemId              = models.ForeignKey(Item, on_delete=models.PROTECT,related_name='item_id_bundleItems', null=True)
    quantity            = models.IntegerField()
    priority            = models.IntegerField(null=True)
    status              = models.IntegerField(null=False, choices=status_choice, default=ACTIVE)
    history = CustomHistoricalRecords()

    class Meta:
        db_table = "bundle_items"

############### WISHLIST MODEL ################

class Wishlist(models.Model):

    id          =   models.BigAutoField(primary_key=True)
    user        =   models.ForeignKey(User, on_delete=models.PROTECT,related_name='IUser_id', null=True)
    item        =   models.ForeignKey(Item, on_delete=models.PROTECT,related_name='Item_Product_id', null=True)
    timestamp   =   models.DateTimeField(default=timezone.now, null=True)
    history = CustomHistoricalRecords()

    class Meta:
        db_table = "cus_wishlist"

###################### PUBLISHER MODEL #######################

# class Publisher(models.Model):
#     ACTIVE      = 1
#     INACTIVE    = 2
#     DELETED     = 3
#     status_choice = ((ACTIVE, "ACTIVE"), (INACTIVE, "INACTIVE"), (DELETED, "DELETED"))

#     id                  = models.BigAutoField(primary_key=True)
#     name                = models.CharField(max_length=100,null=False)
#     slug                = models.CharField(max_length=150,null=True)
#     timestamp           = models.DateTimeField(default=timezone.now, null=True)
#     status              = models.IntegerField(null=False, choices=status_choice, default=ACTIVE)

#     class Meta:
#         db_table = "publisher"

##################### AUTHOR MODEL #######################

# class Author(models.Model):
#     ACTIVE      = 1
#     INACTIVE    = 2
#     DELETED     = 3
#     status_choice = ((ACTIVE, "ACTIVE"), (INACTIVE, "INACTIVE"), (DELETED, "DELETED"))

#     id                  = models.BigAutoField(primary_key=True)
#     name                = models.CharField(max_length=100,null=False)
#     slug                = models.CharField(max_length=150,null=True)
#     timestamp           = models.DateTimeField(default=timezone.now, null=True)
#     status              = models.IntegerField(null=False, choices=status_choice, default=ACTIVE)

#     class Meta:
#         db_table = "author"

################### SLIDER MODEL #########################

# class Slider(models.Model):
#     ACTIVE      = 1
#     INACTIVE    = 2
#     DELETED     = 3
#     status_choice = ((ACTIVE, "ACTIVE"), (INACTIVE, "INACTIVE"), (DELETED, "DELETED"))

#     id                  = models.BigAutoField(primary_key=True)
#     sliderOrder         = models.IntegerField(null=True)
#     sliderImage         = models.ImageField(upload_to='slider_images/', null=False)
#     sliderText          = models.CharField(max_length=150,null=True)
#     sliderUrl           = models.CharField(max_length=150,null=True)
#     # timestamp          = models.DateTimeField(default=timezone.now, null=True)
#     status              = models.IntegerField(null=False, choices=status_choice, default=ACTIVE)

#     class Meta:
#         db_table = "slider"

################ STORE MODEL #########################

# class Store(models.Model):
#     ACTIVE      = 1
#     INACTIVE    = 2
#     DELETED     = 3
#     status_choice = ((ACTIVE, "ACTIVE"), (INACTIVE, "INACTIVE"), (DELETED, "DELETED"))

#     id                  = models.BigAutoField(primary_key=True)
#     name                = models.CharField(max_length=150,null=False)
#     address             = models.CharField(max_length=200,null=True)
#     city                = models.CharField(max_length=100,null=True)
#     zipCode             = models.CharField(max_length=100,null=True)
#     latitude            = models.CharField(max_length=100,null=True)
#     longitude           = models.CharField(max_length=100,null=True)
#     perKmCharges        = models.IntegerField(null=True)
#     status              = models.IntegerField(null=False, choices=status_choice, default=ACTIVE)

#     class Meta:
#         db_table = "store"

######################### SPONSORED LOGO ######################

# class SponsoredLogo(models.Model):
#     ACTIVE      = 1
#     INACTIVE    = 2
#     DELETED     = 3
#     status_choice = ((ACTIVE, "ACTIVE"), (INACTIVE, "INACTIVE"), (DELETED, "DELETED"))

#     id                  = models.BigAutoField(primary_key=True)
#     image               = models.ImageField(upload_to='sponsored_images/', null=True)
#     link                = models.CharField(max_length=100,null=True)
#     status              = models.IntegerField(null=False, choices=status_choice, default=ACTIVE)

#     class Meta:
#         db_table = "sponsored_logo"

class Order(models.Model):
    UNCONFIRMED     = "UNCONFIRMED"
    PENDING         = "PENDING"
    CONFIRMED       = "CONFIRMED"
    CANCELLED       = "CANCELLED"

    status_choice = ((UNCONFIRMED, "UNCONFIRMED"), (PENDING, "PENDING"), (CONFIRMED, "CONFIRMED"), (CANCELLED, "CANCELLED"))

    BRAND     = 1
    PRODUCT     = 2
    bundle_type = ((BRAND, "BRAND"), (PRODUCT, "PRODUCT"))


    id                  = models.BigAutoField(primary_key=True)
    custId              = models.CharField(max_length = 30, null=True, blank=True) 
    orderNo             = models.CharField(null=False, blank=False, max_length=100)
    custName            = models.CharField(null=True, blank=True, max_length=150)
    custEmail           = models.CharField(null=True, blank=True, max_length=150)
    custPhone           = models.CharField(null=True, blank=True, max_length=150)
    cust_phone2         = models.CharField(null=True, blank=True, max_length=150)
    custCity            = models.CharField(null=True, blank=True, max_length=150)
    shippingAddress     = models.CharField(null=True, blank=True, max_length=500)
    shippingCity        = models.CharField(null=True, blank=True, max_length=150)
    totalBill           = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    discountedBill      = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    deliveryCharges     = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    totalItems          = models.IntegerField(null=True,blank=True)
    paymentMethod       = models.CharField(null=True, blank=True,max_length=30)
    paymentid           =models.CharField(max_length=150,null=True)
    paymentsessionid    =models.CharField(max_length=180,null=True)
    paymentstatus       =models.CharField(max_length=100,null=True)
    paymenttime         =models.DateTimeField(null=True)
    customeronlinepaymentinvoice=models.CharField(max_length=150,null=True)
    deliveryType        = models.CharField(null=True, blank=True,max_length=30)
    timestamp           = models.DateTimeField(default=timezone.now, null=True)
    orderNotification   = models.IntegerField(default=0)
    orderPKPos          = models.IntegerField(null=True)
    status              = models.CharField(null=False, choices=status_choice, default=UNCONFIRMED,max_length=100)
    history = CustomHistoricalRecords()

    class Meta:
        db_table = "order"

    def AddOrder(name, email, phone, phone2, city, address, totalBill,deliveryFee,posStatus):
        try:
            categoryObj = Category.objects.create(custName=name, custEmail=email, custPhone=phone, cust_phone2=phone2, custCity=city, shippingAddress=address, shippingCity=city, totalBill=totalBill, deliveryCharges=deliveryFee, discountedBill=totalBill, paymentMethod='COD')
        except Exception as e:
            print("Exception in AddCategory(model): " + str(e))
        return categoryObj

class OrderDescription(models.Model):
    
    PRODUCT      = 1
    BUNDLE       = 2
    item_type = ((PRODUCT, "PRODUCT"), (BUNDLE, "BUNDLE"))


    id                  = models.BigAutoField(primary_key=True)
    order               = models.ForeignKey(Order, on_delete=models.PROTECT,related_name='order_description_id', null=True)
    item_type           = models.IntegerField(null=False, choices=item_type, default=PRODUCT)
    itemSku             = models.CharField(null=False, blank=False, max_length=100)
    itemName            = models.CharField(null=True, blank=True, max_length=150)
    itemUnit            = models.CharField(null=True, blank=True, max_length=150)
    itemMinQty          = models.IntegerField(null=True, blank=True)
    mrp                 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    salePrice           = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    itemIndPrice        = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    itemTotalPrice      = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    itemQty             = models.IntegerField(null=True, blank=True)
    isStockManaged      = models.BooleanField(default=False)
    isDeleted           = models.BooleanField(default=False)
    history = CustomHistoricalRecords()
    
    class Meta:
        db_table = "order_description"
    

    ##################### Zuhoor Model 11/23/22 ###############################


class IndividualBoxOrder(models.Model):        

    id              = models.BigAutoField(primary_key=True)
    sequenceNo      = models.IntegerField( null=True)
    category        = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='Category', null=True)
    image           = models.CharField(max_length=100,null=True)
    category_slug   =models.CharField(max_length=100,null=True)
    name            =models.CharField(max_length=100,null=True)
    history = CustomHistoricalRecords()
    class Meta:
        db_table = "Individual_BoxOrder"

    def __str__(self):
        return self.image
    
    def Addindorder(mapping):
        obj = IndividualBoxOrder()
        try:
            for (field, value) in (mapping.items()):
                if value:
                    setattr(obj, field,value)
            responseObject = obj.save()
            # return obj
        except IntegrityError:
            # print("Exception in AddCategory(model): " + str(e))
            raise
        return responseObject

class SectionSequence(models.Model):
    
    id              = models.BigAutoField(primary_key=True)
    sequenceNo      = models.IntegerField( null=True)
    category        = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='Category1', null=True)
    child1          = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='Category_child1', null=True)
    child1_name     = models.CharField(max_length=100,null=True)
    child1_slug     = models.CharField(max_length=100,null=True)
    child2          = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='Category_child2', null=True)
    child2_name     = models.CharField(max_length=100,null=True)
    child2_slug     = models.CharField(max_length=100,null=True)
    child3          = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='Category_child3', null=True)
    child3_name     = models.CharField(max_length=100,null=True)
    child3_slug     = models.CharField(max_length=100,null=True)

    child4          = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='Category_child4', null=True)
    child4_name     = models.CharField(max_length=100,null=True)
    child4_slug     = models.CharField(max_length=100,null=True)
    child5          = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='Category_child5', null=True)
    child5_name     = models.CharField(max_length=100,null=True)
    child5_slug     = models.CharField(max_length=100,null=True)
    child6          = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='Category_child6', null=True)
    child6_name     = models.CharField(max_length=100,null=True)
    child6_slug     = models.CharField(max_length=100,null=True)
    child7          = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='Category_child7', null=True)
    child7_name     = models.CharField(max_length=100,null=True)   
    child7_slug     = models.CharField(max_length=100,null=True)
    child8          = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='Category_child8', null=True)
    child8_name     = models.CharField(max_length=100,null=True)    
    child8_slug     = models.CharField(max_length=100,null=True)
    category_slug   = models.CharField(max_length=100,null=True)
    name            = models.CharField(max_length=100,null=True)
    history = CustomHistoricalRecords()

    class Meta:
        db_table = "section_sequence"

    def __str__(self):
        return self.id
    
    def AddSectionSequence(mapping):
        obj = SectionSequence()
        try:
            for (field, value) in (mapping.items()):
                if value:
                    setattr(obj, field,value)
            responseObject = obj.save()
            # return obj
        except IntegrityError:
            # print("Exception in AddCategory(model): " + str(e))
            raise
        return responseObject

class Configuration(models.Model):
    id                  = models.BigAutoField(primary_key=True)
    name                = models.CharField(null=True, blank=True, max_length=100)
    value               = models.CharField(null=True, blank=True, max_length=100)
    location            = models.CharField(null=True, blank=True, max_length=100)
    priority            = models.IntegerField(default=1)
    history = CustomHistoricalRecords()
    class Meta:
        db_table = "configuration"

class Individual_BoxOrder(models.Model):
    id              = models.BigAutoField(primary_key=True)
    sequenceNo      = models.IntegerField( null=True)
    image           = models.CharField(max_length=100,null=True)
    category_id     = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='Category2', null=True)
    category_slug   = models.CharField(max_length=100,null=True)
    category_name   = models.CharField(max_length=100,null=True)
    type            = models.CharField(max_length=100,null=True)
    parent          = models.IntegerField(null=True)
    class Meta:
        db_table = "IndividualBoxOrder"


########## Token Blacklist Model ##########

class TokenBlacklist(models.Model):
    token = models.CharField(max_length=500)
    blacklisted_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = "token_blacklist"
    def __str__(self):
        return self.token

class DynamicText(models.Model):
    ACTIVE    = 1
    INACTIVE  = 2
    DELETED   = 3
    status_choice = ((ACTIVE, "ACTIVE"), (INACTIVE, "INACTIVE"), (DELETED, "DELETED"))

    id          = models.BigAutoField(primary_key=True)
    key         = models.CharField(max_length=101, null=False)
    value       = models.TextField(null=False)
    status      = models.IntegerField(null=False, choices=status_choice, default=ACTIVE)
    
    class Meta:
        db_table = "dynamic_text"





class SiteSettings(models.Model):
    
    # General 
    site_logo = models.ImageField(upload_to='sitesetting/', null=True, blank=True)
    site_name = models.CharField(max_length=100)
    site_metatitle=models.CharField(max_length=500,null=True)
    site_description = models.TextField()
    site_banner_text = models.CharField(max_length=100)
    site_banner_image = models.ImageField(upload_to='sitesetting/', null=True, blank=True)
    site_splash=models.ImageField(upload_to='sitesetting/', null=True, blank=True)
    splashtime=models.IntegerField(null=True)
    currency=models.CharField(max_length=100,null=True)
    # TopBar 
    top_bar_left_phone = models.CharField(max_length=20)
    top_bar_left_email = models.EmailField()
    top_bar_right_items = models.ManyToManyField('TopBarRightItem')

    # Footer 
    footer_logo = models.ImageField(upload_to='sitesetting/', null=True, blank=True)
    footer_description = models.TextField()
    footer_second_column_heading = models.CharField(max_length=100)
    footer_third_column_heading = models.CharField(max_length=100)
    footer_second_column_items = models.ManyToManyField('FooterColumnItem', related_name='second_column_items')
    footer_third_column_items = models.ManyToManyField('FooterColumnItem', related_name='third_column_items')
    footer_fourth_column_heading = models.CharField(max_length=100)
    footer_fourth_column_content = models.TextField()

    # Social Links 
    facebook = models.URLField(null=True, blank=True)
    twitter = models.URLField(null=True, blank=True)
    instagram = models.URLField(null=True, blank=True)
    youtube = models.URLField(null=True, blank=True)
    app_links = models.URLField(null=True, blank=True)
    app_store = models.ImageField(upload_to='sitesetting/', null=True, blank=True)
    googleid=models.CharField(max_length=300,null=True)
    googlesecret=models.CharField(max_length=300,null=True)
    facebookid=models.CharField(max_length=300,null=True)
    facebooksecret=models.CharField(max_length=300,null=True)
    ###############Shipping##########################################

    shipping=models.IntegerField(default=300,null=True)

    ##########################Whatsapp#########################
    whatsapp= models.CharField(null=True, blank=True, max_length=150)


    class Meta:
        db_table = "site_setting"



class TopBarRightItem(models.Model):
    site_settings = models.ForeignKey(SiteSettings, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    priority    = models.IntegerField(default=1)
    link = models.URLField()

    class Meta:
        db_table = "topbar_item"


class FooterColumnItem(models.Model):
    site_settings = models.ForeignKey(SiteSettings, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    priority    = models.IntegerField(default=1)
    link = models.URLField()
    column=models.IntegerField()

    class Meta:
        db_table = "footer_item"
class SiteImage(models.Model):
    site_settings = models.ForeignKey(SiteSettings, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='sitesetting/slider/', null=True, blank=True)

    class Meta:
        db_table = "slider_image"



class DashboardStatistics(models.Model):
    Last30days= 1
    Currentmonth= 2
    stat_type = ((Last30days, "Last30days"), (Currentmonth, "Currentmonth"))
    id=models.BigAutoField(primary_key=True)
    name=models.CharField(max_length=100)
    value=models.IntegerField()
    stat_type=models.IntegerField(null=False,choices=stat_type,default=Currentmonth)
    updatetime= models.DateTimeField(default=timezone.now, null=True)

    class Meta:
        db_table = "dashboard_statistics"




class ProductReview(models.Model):
    username = models.CharField(max_length=100)
    userid = models.ForeignKey(User, on_delete=models.CASCADE)
    itemid = models.ForeignKey(Item, on_delete=models.CASCADE)
    itemname=models.CharField(max_length=222,null=True)
    rating = models.IntegerField(default=0)
    review = models.TextField()
    date   = models.DateTimeField(null=True)
    class Meta:
        db_table = "product_review"




class Voucher(models.Model):
    ACTIVE    = 'ACTIVE'
    INACTIVE  = 'INACTIVE'
    status_choice = ((ACTIVE, "ACTIVE"), (INACTIVE, "INACTIVE"))


    id  = models.BigAutoField(primary_key=True)
    name=models.CharField(max_length=200)
    image=models.ImageField(upload_to='vouchers/', null=True, blank=True)
    code=models.CharField(max_length=100)
    discount = models.DecimalField(max_digits=5, decimal_places=2)
    status=models.IntegerField(null=False, choices=status_choice, default=ACTIVE)
    startdate=models.DateTimeField()
    enddate=models.DateTimeField()

    class Meta:
        db_table = "voucher"


class UserVoucher(models.Model):

    id=models.BigAutoField(primary_key=True)
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    voucher=models.ForeignKey(Voucher, on_delete=models.CASCADE)
    vouchercode=models.CharField(max_length=200,null=True)
    isused=models.BooleanField(default=False)
    class Meta:
        db_table = "uservoucher"



class Courier(models.Model):
    id=models.BigAutoField(primary_key=True)
    name=models.CharField(max_length=100)
    country=models.ForeignKey(Country,on_delete=models.CASCADE)
    countryname=models.CharField(max_length=100,null=True)
    time=models.CharField(max_length=200)
    price=models.CharField(max_length=100)
    class Meta:
        db_table = "courier"

class CourierConfiguration(models.Model):
    ACTIVE    = 'ACTIVE'
    INACTIVE  = 'INACTIVE'
    DELETED   = 'DELETED'
    status_choice = ((ACTIVE, "ACTIVE"), (INACTIVE, "INACTIVE"), (DELETED, "DELETED"))
    SAME    = 'SAME'
    MAJOR   = 'MAJOR'
    OTHER   = 'OTHER'
    type_choices = ((SAME, 'SAME'),(MAJOR, 'MAJOR'),(OTHER, 'OTHER'),)

    id          = models.BigAutoField(primary_key=True)
    cityType    = models.CharField(max_length=100, choices=type_choices, default=OTHER)
    weight      = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    price       = models.IntegerField()
    addOn       = models.BooleanField(default=False)
    courier     = models.ForeignKey(Courier, on_delete=models.PROTECT,null=True )
    couriername=models.CharField(max_length=100)
    status      = models.CharField(max_length=100, choices=status_choice, default=ACTIVE)
    class Meta:
        db_table = "courier_configuration"



