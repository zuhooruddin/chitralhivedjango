from inara.models import *
from rest_framework import serializers

from django.contrib.auth import get_user_model, authenticate
from django.conf import settings
# from django.utils.translation import ugettext_lazy as _
from django.utils.translation import gettext as _
from rest_framework import serializers, exceptions
from rest_framework.exceptions import ValidationError
from allauth.account import app_settings
from dj_rest_auth.serializers import PasswordResetSerializer
import os

UserModel = get_user_model()


class CustomLoginRoleSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(style={'input_type': 'password'})
    role    = serializers.IntegerField()
  
    print("custom user login")
    def authenticate(self, **kwargs):
        return authenticate(self.context['request'], **kwargs)

    def _validate_email(self, email, password):
        user = None
        print("CustomLoginRoleSerializer _validate_email ")
        if email and password:
            user = self.authenticate(email=email, password=password)
        else:
            msg = _('Must include "email" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def _validate_username(self, username, password):
        user = None
        print("CustomLoginRoleSerializer _validate_username ")
        if username and password:
            user = self.authenticate(username=username, password=password)
        else:
            msg = _('Must include "username" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def _validate_username_email(self, username, email, password):
        user = None
        print("CustomLoginRoleSerializer _validate_username_email ")
        if email and password:
            user = self.authenticate(email=email, password=password)
        elif username and password:
            user = self.authenticate(username=username, password=password)
        else:
            msg = _('Must include either "username" or "email" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def validate(self, attrs):
        print("CustomLoginRoleSerializer validate ")
        username = attrs.get('username')
        email = attrs.get('email')
        password = attrs.get('password')
        role = attrs.get('role')

        print(attrs.get('role'))

        user = None

        if 'allauth' in settings.INSTALLED_APPS:
            from allauth.account import app_settings
            print("app_settings.AUTHENTICATION_METHOD: ",app_settings.AUTHENTICATION_METHOD)

            # Authentication through email
            if app_settings.AUTHENTICATION_METHOD == app_settings.AuthenticationMethod.EMAIL:
                user = self._validate_email(email, password)

            # Authentication through username
            elif app_settings.AUTHENTICATION_METHOD == app_settings.AuthenticationMethod.USERNAME:
                user = self._validate_username(username, password)

            # Authentication through either username or email
            else:
                user = self._validate_username_email(username, email, password)
            # print("user from allauth :",user)
        else:
            # Authentication without using allauth
            if email:
                try:
                    username = UserModel.objects.get(email__iexact=email).get_username()
                except UserModel.DoesNotExist:
                    pass

            if username:
                user = self._validate_username_email(username, '', password)
            # print("user from allauth else: :",user)
        # Did we get back an active user?
        
        if user:
            if not user.is_active:
                msg = _('User account is disabled or user is not authorized.')
                raise exceptions.ValidationError(msg)
        else:
            msg = _('Unable to log in with provided credentials.')
            raise exceptions.ValidationError(msg)
        if user:
            print("User Role is",user.role)
            if  user.role != role:
                msg = _('User account is not authorized to use this portal.')
                raise exceptions.ValidationError(msg)
        else:
            msg = _('Unable to log in with provided credentials.')
            raise exceptions.ValidationError(msg)

        # If required, is the email verified?
        if 'rest_auth.registration' in settings.INSTALLED_APPS:
            
            if app_settings.EMAIL_VERIFICATION == app_settings.EmailVerificationMethod.MANDATORY:
                email_address = user.emailaddress_set.get(email=user.email)
                if not email_address.verified:
                    raise serializers.ValidationError(_('E-mail is not verified.'))

        attrs['user'] = user
        return attrs

class wishListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = '__all__'
        # depth = 2

class WishListUserItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = ['item']
        # depth = 2

class UserModelSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    extra_kwargs = {'password': {'write_only': True}}
    fields = [
      "id",
      "name",
      "username",
      "email",
      "password",
      "role",
    ]

  def create(self, validated_data):
    user = UserModel.objects.create_user(
      validated_data["username"],
      validated_data["email"],  
      validated_data["password"]
    )

    return user
################################External Category###########################################################
class CategorySerializer(serializers.ModelSerializer):
    # parentId_name = serializers.CharField(source='name')
    class Meta:
        model = Category
        fields = ('id','extPosId','extPosParentId','parentId','name','slug','description','icon','appliesOnline','syncTs','metaUrl','metaTitle','metaDescription','isBrand','posType','status')


################################Local Category###########################################################
# class LocalCategorySerializer(serializers.ModelSerializer):
#     # parentId_name = serializers.CharField(source='name')
#     class Meta:
#         model =LocalCategory
#         fields = '__all__'




class CategorySerializerDepth(serializers.ModelSerializer):
    # parentId_name = serializers.CharField(source='name')
    class Meta:
        model = Category
        fields = ('id','extPosId','extPosParentId','parentId','name','slug','description','icon','appliesOnline','syncTs','metaUrl','metaTitle','metaDescription','isBrand','posType','status')
        depth = 1


class ItemSerializer(serializers.ModelSerializer):
    # Remove SerializerMethodField to allow image uploads
    # ImageField will automatically return the URL when reading
    # and accept file uploads when writing
    class Meta:
        model = Item
        fields = '__all__'
        # depth = 2
    
    def to_representation(self, instance):
        # Get the default representation
        representation = super().to_representation(instance)
        # Ensure image returns the full URL when reading
        if instance.image:
            representation['image'] = instance.image.url
        return representation

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        # depth = 2



class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
        # depth = 2
class OrderDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDescription
        fields = '__all__'
        # depth = 2

class ItemGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemGallery
        fields = '__all__'
        # depth = 2

class BundleSerializer(serializers.ModelSerializer):
    # image = serializers.SerializerMethodField('get_image_url')
    class Meta:
        model = Bundle
        fields = '__all__'
        # depth = 2
    def get_image(self, obj):
        image_name = os.path.basename(obj.image.url)
        return obj.image.name

class BundleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BundleItem
        fields = '__all__'
        # depth = 2

class MyModelSerializer(serializers.ModelSerializer):

    # creator = serializers.ReadOnlyField(source='creator.username')
    # creator_id = serializers.ReadOnlyField(source='creator.id')
    # image = serializers.ImageField(required=False)

    class Meta:
        model = Item
        fields = '__all__'


class IndividualBoxOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model =IndividualBoxOrder
        fields = [
        "id",
        "sequenceNo",
        "category",
        "image",
        "category_slug",
        "name"
    ]
    def create(self, validated_data):
      indorder = IndividualBoxOrder.objects.create(
        validated_data["id"],
        validated_data["sequenceNo"],
        validated_data["category"] ,
        validated_data["image"],
        validated_data["category_slug"],
        validated_data["name"]
    )
      return indorder

class SectionSequenceSerializer(serializers.ModelSerializer):
    class Meta:
        model =SectionSequence
        fields = [
        "id",
        "sequenceNo",
        "category",
        "child1",
        "child1_name",
        "child1_slug",
        "child2",
        "child2_name",
        "child2_slug",
        "child3",
        "child3_name",
        "child3_slug",
        "child4",
        "child4_name",
        "child4_slug",
        "child5",
        "child5_name",
        "child5_slug",
        "child6",
        "child6_name",
        "child6_slug",
        "child7",
        "child7_name",
        "child7_slug",
        "child8",
        "child8_name",
        "child8_slug",
        "category_slug",
        "name"
    ]
    def create(self, validated_data):
      sectionsequence = SectionSequence.objects.create(
        validated_data["id"],
        validated_data["sequenceNo"],
        validated_data["category"] ,
        validated_data["child1"],
        validated_data["child1_name"],
        validated_data["child1_slug"],
        validated_data["child2"],
        validated_data["child2_name"],
        validated_data["child2_slug"],
        validated_data["child3"],
        validated_data["child3_name"],
        validated_data["child3_slug"],
        validated_data["child4"],
        validated_data["child4_name"],
        validated_data["child4_slug"],
        validated_data["child5"],
        validated_data["child5_name"],
        validated_data["child5_slug"],
        validated_data["child6"],
        validated_data["child6_name"],
        validated_data["child6_slug"],
        validated_data["child7"],
        validated_data["child7_name"],
        validated_data["child7_slug"],
        validated_data["child8"],
        validated_data["child8_name"],
        validated_data["child8_slug"],
        validated_data["category_slug"],
        validated_data["name"] 
    )
      return sectionsequence
  
class CategoryItemSerializers(serializers.ModelSerializer):
    class Meta:
        model = CategoryItem
        fields = '__all__'

class TaskProgressSerializers(serializers.ModelSerializer):
    class Meta:
        model = TaskProgress
        fields = '__all__'

class ShippingSerializers(serializers.ModelSerializer):
    class Meta:
        model = UserShippingDetail
        fields = '__all__'

class ConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Configuration
        fields = '__all__'

class CustomPasswordResetSerializer(PasswordResetSerializer):
    def get_email_options(self):
        return{
            'html_email_template_name':'registration/custom_reset_confirm.html',
        }

class ConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Configuration
        fields = '__all__'

class IndividualBoxOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Individual_BoxOrder
        fields = '__all__'

class DynamicTextSerializer(serializers.ModelSerializer):
    class Meta:
        model = DynamicText
        fields = '__all__'

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'
class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'
class CourierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Courier
        fields = '__all__'

class CourierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Courier
        fields = '__all__'

class CourierConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourierConfiguration
        fields = '__all__'

class CourierConfigurationSerializerDepth(serializers.ModelSerializer):
    class Meta:
        model = CourierConfiguration
        fields = '__all__'
        depth = 1