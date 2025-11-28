from os import stat
from inara.models import User,UserShippingDetail
from django.http import JsonResponse
from rest_framework.response import Response
import json
import re
from unidecode import unidecode
from django.db import IntegrityError


class RPOS7Customers(object):	
    extPosId    = None
    name        = None
    # password    = None
    email       = None
    username    = None
    phone       = None
    mobile      = None
    address     = None
    city        = None
    area        = None
    status      = None
    role        = None
    
    def reset(self):
        self.name       = None
        # self.password   = None
        self.email      = None
        self.username   = None
        self.phone      = None
        self.mobile     = None
        self.address    = None
        self.city       = None
        self.area       = None
        self.status     = None
        self.role       = None


class RPOS7CustomersSync(object):

    def syncCustomers(self):
        context = {}
        # r=requests.get("https://722157.true-order.com/WebReporter/api/v1/categories", headers={"X-Auth-Token":"9BAA1E819AD48254DFF928F5012BBD95585D2E068EC93AED4DA0810AC0D649BE35F51CE2432EA204"})
        # json_data = r.json()
        # print(r.request.headers)
        # with open('categories.json', 'w') as json_file:
        #     json.dump(json_data, json_file)
        with open('customers.json', 'r') as f:
            jsonObj = json.load(f)
        try:
            for customers in jsonObj['eCustomers']:
                # if (categories['catName'] == 'Cat1') or (categories['catName'] == 'Cat2'):
                    # mapping_dict contains sync fields (update/create) from external pos
                # for value in customers['categoryValues']:
                obj = RPOS7Customers()
                # if value['appliesOnline'] == 1:
                #   status = Category.INACTIVE
                role = User.CUSTOMER
                if customers['status'] == "A":
                    status = User.ACTIVE
                else:
                    status = User.INACTIVE
                if User.objects.filter(extPosId=customers['id']).exists():
                    pass
                else:
                    # Category.AddCategory(value['categoryValueId'], value['parentId'], value['categoryValueName'], value['description'], value['appliesOnline'], value['syncTs'], value['lovSequence'], status,Category.EXTERNAL)
                    obj.extPosId    = customers['id']
                    obj.name        = customers['name']
                    obj.email       = customers['email']
                    # obj.username    = customers['username']
                    obj.phone       = customers['phone2']
                    obj.mobile      = customers['mobile']
                    obj.address     = customers['address1']
                    # obj.city        = customers['city']
                    # obj.area        = customers['area']
                    obj.status      = status
                    obj.role        = role
                    try:
                        customerObject  = User.AddUser(obj.__dict__)
                        if UserShippingDetail.objects.filter(user = customerObject.pk).exists():
                            pass
                        else:
                            shippingObject  = UserShippingDetail.objects.create(user = customerObject,area=customers['area'],address=obj.address,city=customers['city'])
                    except IntegrityError as error:
                        print("Exception in eCustomers gofrugle " + str(error))
                    
                    # if customerObject.extPosParentId == 0:
                    #     pass
                    # else:
                    #     posObject       = Category.objects.get(extPosId=catObject.extPosParentId)
                    #     Category.objects.filter(id=catObject.pk).update(parentId=posObject.pk)

                                
        except Exception as e:
            print("Exception in SyncCustomers - RPOS7: " + str(e))

        return JsonResponse({'errorcode':'success'})