from django.urls import path,include
from . import views
from inara.views import  PaginatedCategory,updateChargesConfiguration,getWebsitePagniatedBundlesForCategory,getAllCourierConfiguration,getAllCourier,updateCountryConfiguration,updateCityConfiguration,getAllCity,getAllCountry,getAllLocalPaginatedCategories,getSearchCategory,updateItem,getAllBrand,getAllBrandBundle,getAllProductBundle,updateItemGallery,getAllPaginatedItems,getAllPaginatedCategories, addCategory,updateCategory, addBrand, updateBrand, addBundle,updateBundle, PostListDetailfilter, updateConfiguration, getAllCustomers,getAllPaginatedItemsForBundle,getAllInternalPaginatedItemsForBundle,getAllWebsitePaginatedItem,getAllOrder,updateAdminImage
from django.contrib import admin
from .views import GoogleLoginView
from rest_framework.routers import DefaultRouter
from dj_rest_auth.views import PasswordResetConfirmView
from dj_rest_auth.views import PasswordChangeView
from rest_framework_simplejwt.views import TokenBlacklistView
# from inara.views import CustomTokenRefreshView

#webApi FrontEnd
#api    Backend

router = DefaultRouter()

urlpatterns = [ 

    # Dummy Sync Item urls
    path("google/", GoogleLoginView.as_view(), name = "google"),
    path('api/auth/password/reset/confirm/<str:uidb64>/<str:token>', PasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    path('api/auth/password/change/<str:uidb64>/<str:token>', PasswordChangeView.as_view(),name='password_change'),
    # path('api/auth/token/refresh', views.BlacklistRefreshView.as_view(), name="token_refresh"),
    # path('api/token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    # path('api/auth/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),

    path('api/auth/', include('dj_rest_auth.urls')),

    # Blacklist Access Tokken
    path('apiSignOut', views.apiSignOut, name = 'apiSignOut'),

    # Sync Categories And Item From FrontEnd
    # path('adminSyncItems', views.adminSyncItems, name = 'adminSyncItems'),
    path('adminSyncCategories', views.adminSyncCategories, name = 'adminSyncCategories'),
    path('categoriesTaskProgress', views.categoriesTaskProgress, name = 'categoriesTaskProgress'),
    path('adminSyncItems', views.adminSyncItems, name = 'adminSyncItems'),
    path('itemsTaskProgress', views.itemsTaskProgress, name = 'itemsTaskProgress'),
    path('stopTaskSync', views.stopTaskSync, name = 'stopTaskSync'),

    # Idrisbookbank Admin Panel
    path('getAllPaginatedCategories', getAllPaginatedCategories.as_view(), name = 'getAllPaginatedCategories'),
    path('getAllLocalPaginatedCategories', getAllLocalPaginatedCategories.as_view(), name = 'getAllLocalPaginatedCategories'),

    

    path('getAllCategories', views.getAllCategories, name = 'getAllCategories'),
    path('getAllLocalCategories', views.getAllLocalCategories, name = 'getAllLocalCategories'),


   
    path('getCategory', views.getCategory, name = 'getCategory'),
    path('getLocalCategory', views.getLocalCategory, name = 'getLocalCategory'),


 
    path('getmyCategories', views.getmyCategories, name = 'getmyCategories'), 
    # path('getNavCategories', views.getNavCategories, name = 'getNavCategories'),
    path('getProductCategories', views.getProductCategories, name = 'getProductCategories'),
    path('getCusWishlists', views.GetWishlists, name = 'getCusWishlists'),

    path('getLocalProductCategories', views.getLocalProductCategories, name = 'getLocalProductCategories'),

   
    path('getParentCategories', views.getParentCategories, name = 'getParentCategories'),
    path('getLocalParentCategories', views.getLocalParentCategories, name = 'getLocalParentCategories'),


    
    path('getSubCategories', views.getSubCategories, name = 'getSubCategories'),
    path('getLocalSubCategories', views.getLocalSubCategories, name = 'getLocalSubCategories'),



   
    path('getSearchCategory', getSearchCategory.as_view(), name = 'getSearchCategory'),
    path('PaginatedCategory', PaginatedCategory.as_view(), name = 'PaginatedCategory'),
    path('PaginatedCategorys',views.get_all_paginated_items, name = 'PaginatedCategorys'),

    path('addCategory',  addCategory.as_view(), name = 'addCategory'),

 
    path('updateCategory/<int:pk>',  updateCategory.as_view(), name = 'updateCategory'),

    
    path('checkCategoryChange', views.checkCategoryChange, name = 'checkCategoryChange'),
    path('deleteCategory',  views.deleteCategory, name = 'deleteCategory'),




    ########### Website API's ############################################
    path('getNavCategories', views.getNavCategories, name = 'getNavCategories'), # used

    path('getLocalNavCategories', views.getLocalNavCategories, name = 'getLocalNavCategories'), # used








    path('showAllNavCategories', views.showAllNavCategories, name = 'showAllNavCategories'), # used
    path('getItemDetail', views.getItemDetail, name = 'getItemDetail'), # used
    path('getCategoryDetail', views.getCategoryDetail, name = 'getCategoryDetail'), # used

    ########## Sliders API #############
    path('getSlidersFromCloud', views.getSlidersFromCloud, name = 'getSlidersFromCloud'), # used



    ##### Items #####
    path('syncItems', views.syncItems, name = 'syncItems'),
    path('getAllPaginatedItems', getAllPaginatedItems.as_view(), name = 'getAllPaginatedItems'),
    path('getAllPaginatedItemsForBundle', getAllPaginatedItemsForBundle.as_view(), name = 'getAllPaginatedItemsForBundle'),
    path('getAllInternalPaginatedItemsForBundle',getAllInternalPaginatedItemsForBundle.as_view(), name = 'getAllInternalPaginatedItemsForBundle'),
    path('getAllItems', views.getAllItems, name = 'getAllItems'),
    path('getItem', views.getItem, name = 'getItem'),
    path('getItemCategory', views.getItemCategory, name = 'getItemCategory'),
    path('getItemGallery', views.getItemGallery, name = 'getItemGallery'),
    path('getSearchItem', views.getSearchItem, name = 'getSearchItem'),
    path('updateItem/<int:pk>',  updateItem.as_view(), name = 'updateItem'),
    path('updateItemGallery/<int:pk>',  views.updateItemGallery, name = 'updateItemGallery'),
    path('updateItemCategory/<int:pk>',  views.updateItemCategory, name = 'updateItemCategory'),




    
    #### Bundles #############
    path('getAllBrandBundle', getAllBrandBundle.as_view(), name = 'getAllBrandBundle'),
    path('getAllProductBundle', getAllProductBundle.as_view(), name = 'getAllProductBundle'),
    path('addBundle',  addBundle.as_view(), name = 'addBundle'),
    path('updateBundle/<int:pk>',  updateBundle.as_view(), name = 'updateBundle'),
    path('deleteBundle',  views.deleteBundle, name = 'deleteBundle'),
    path('updatePriorityBundleItem',  views.updatePriorityBundleItem, name = 'updatePriorityBundleItem'),


    path('getWebsiteBundlesForCategory',  views.getWebsiteBundlesForCategory, name = 'getWebsiteBundleItems'),
    path('getWebsiteBundleItemDetails',  views.getWebsiteBundleItemDetails, name = 'getWebsiteBundleItemDetails'),
    path('getWebsitePagniatedBundlesForCategory', getWebsitePagniatedBundlesForCategory.as_view(), name = 'getWebsitePagniatedBundlesForCategory'),
    path('getAllWebsitePaginatedItem', getAllWebsitePaginatedItem.as_view(), name = 'getAllWebsitePaginatedItem'),
    path('getAllWebsitePaginatedItems', views.get_all_website_paginated_item, name = 'getAllWebsitePaginatedItem'),


    path('getBundle',  views.getBundle, name = 'getBundle'),
    path('getBundleItemsForAdminConfiguration',  views.getBundleItemsForAdminConfiguration, name = 'getBundleItemsForAdminConfiguration'),
    path('getBundleForAdminConfiguration',  views.getBundleForAdminConfiguration, name = 'getBundleForAdminConfiguration'),
    path('updateBundleItemPriority',  views.updateBundleItemPriority, name = 'updateBundleItemPriority'),
    path('getBundleTypes',  views.getBundleTypes, name = 'getBundleTypes'),
    path('getBundleForPrioritySet',  views.getBundleForPrioritySet, name = 'getBundleForPrioritySet'),
    path('updateBundlePriority',  views.updateBundlePriority, name = 'updateBundlePriority'),
    path('addBundleItem',  views.addBundleItem, name = 'addBundleItem'),
    path('updateBundleItem',  views.updateBundleItem, name = 'updateBundleItem'),
    path('getAllBrand', getAllBrand.as_view(), name = 'getAllBrand'),
    path('getBrand', views.getBrand, name = 'getBrand'),
    path('addBrand',  addBrand.as_view(), name = 'addBrand'),
    path('updateBrand/<int:pk>',  updateBrand.as_view(), name = 'updateBrand'),
    path('deleteBrand',  views.deleteBrand, name = 'deleteBrand'),





    #### Admin/User   ##############
    path('addAdmin', views.addAdmin, name = 'addAdmin'),
    path('updateAdmin', views.updateAdmin, name = 'updateAdmin'),
    path('updateAdminProfile', views.updateAdminProfile, name = 'updateAdminProfile'),
    path('updateAdminImage/<int:pk>',  updateAdminImage.as_view(), name = 'updateAdminImage'),
    path('getAllAdmin', views.getAllAdmin, name = 'getAllAdmin'),
    path('getAdmin', views.getAdmin, name = 'getAdmin'),
    path('deleteAdmin', views.deleteAdmin, name = 'deleteAdmin'),



    #### Customers    ###############
    path('getAllCustomers', getAllCustomers.as_view(), name = 'getAllCustomers'),
    path('syncCustomers', views.syncCustomers, name = 'syncCustomers'),

    #### Order #######################################
    path('addOrder', views.addOrder, name = 'addOrder'),
    path('getAllOrder', getAllOrder.as_view(), name = 'getAllOrder'),
    path('getOrder', views.getOrder, name = 'getOrder'),
    path('getOrderProduct', views.getOrderProduct, name = 'getOrderProduct'),
    path('updateOrder', views.updateOrder, name = 'updateOrder'),
    path('getCustomerOrders', views. getCustomerOrder, name = 'getCustomerOrders'),
    path('getCustomerOrdersDes', views. getCustomerOrdersDes, name = 'getCustomerOrdersDes'),
    path('getOrderDetails', views. getOrderDetails, name = 'getOrderDetails'),
    path('getAllOrderNotification', views. getAllOrderNotification, name = 'getAllOrderNotification'),
    path('seenOrderNotification', views.seenOrderNotification, name = 'seenOrderNotification'),
    path('getOrderSentToPosDetails', views.getOrderSentToPosDetails, name='getOrderSentToPosDetails'),
    path('saveOrderDB', views.saveOrderDB, name='saveOrderDB'),



    
    ############### ZUHOOR URLS ##################
    #### Shipping Details  ##############
    path('getCustomerShipping', views.getCustomerShipping, name = 'getCustomerShipping'),
    path('deleteCustomerShipping', views.deleteCustomerShipping, name = 'deleteCustomerShipping'),

    #### WishList  ##############
    path('updateWishlist', views.updateWishlist, name = 'updateWishlist'),
    path('getWishlist', views.getWishlist, name = 'getWishlist'),
    path('getWishlists', views.cusGetWishlists, name = 'getWishlists'),


    #### Individual Order   ##############
    path('indorder', views.addIndividualBoxOrder, name = 'indorder'),
    path('getindorder', views.getAllIndividualOrder, name = 'getindorder'),

     #### Section Sequence   ##############
    path('sectionsequence', views.addSectionSequence, name = 'sectionsequence'),
    path('getsection', views.getAllSectionSequence, name = 'getsection'),


    #########Product Category####################
    #  path('getSearchCategory', views.getSearchCategory, name = 'getSearchCategory'),
    path('getItemSearchCategory', views.getItemSearchCategory, name = 'getItemSearchCategory'),
    path('getFearuredProduct',views.getFeaturedItems,name='getFearuredProduct'),

    path('getBundels',views.getBundels,name='getBundels'),
    path('getBrandBundels',views.getBrandBundels,name='getBrandBundels'),
    path('getProductBundels',views.getProductBundels,name='getProductBundels'),

    path('search', PostListDetailfilter.as_view(), name='postsearch'),

    path('registerUser',views.registerUser,name='registerUser'),
    path('resetpassword', views.resetpassword,name='rest_password_reset'),
    # path('reset/<uid>/<token>/', MyPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
############## homePage ##############################################

    path('AllIndividualBoxOrder', views.AllIndividualBoxOrder, name='AllIndividualBoxOrder'),
    path('AllCategories', views.AllCategories, name='AllCategories'),
    path('addConfiguration',  views.addConfiguration, name = 'addConfiguration'),
    path('addIndividual_BoxOrder',  views.addIndividual_BoxOrder, name = 'addIndividual_BoxOrder'),
    path('AllSectionSequence',  views.AllSectionSequence, name = 'AllSectionSequence'),
    path('AllConfiguration',  views.AllConfiguration, name = 'AllConfiguration'),
    path('getConfiguration',  views.getConfiguration, name = 'getConfiguration'),
    path('updateConfiguration/<int:pk>',  updateConfiguration.as_view(), name = 'updateConfiguration'),
    path('checkConfigurationChange', views.checkConfigurationChange, name = 'checkConfigurationChange'),
    path('IndividualBoxOrder_Post', views.IndividualBoxOrder_Post, name='IndividualBoxOrder_Post'),
    path('IndividualBoxOrder_Update', views.IndividualBoxOrder_Update, name='IndividualBoxOrder_Update'),
    path('SyncObjectStorageItemImages', views.SyncObjectStorageItemImages, name='SyncObjectStorageItemImages'),
    path('ResetIsNewArrival', views.ResetIsNewArrival, name='ResetIsNewArrival'),
    path('webind', views.BoxOrder, name='webind'),
    path('dynamictext', views.adddynamictext, name='dynamictext'),
    path('get_dynamictext', views.get_dynamic_text, name='get_dynamictext'),
    path('getalldynamictext', views.get_all_dynamic_text, name='getalldynamictext'),
    path('updatedynamictext', views.update_dynamic_text, name='updatedynamictext'),
    path('deletedynamictext', views.delete_dynamic_text, name='deleteDynamicText'),



    path('addItemCategory', views.addItemCategory, name='addItemCategory'),

    path('addItemGallery', views.addItemGallery, name='addItemGallery'),
    path('addItem', views.addItem, name='addItem'),

    path('addsitesetting', views.addSiteSetting, name='addsitesetting'),

    path('getsliderimage', views.getLocalSlider, name='getsliderimage'),
    path('getFooterSettings', views.getFooterSettings, name='getFooterSettings'),
    path('getGeneralSetting', views.getGeneralSetting, name='getGeneralSetting'),
    path('getStatistics', views.getStatistics, name='getStatistics'),
    path('addReviews', views.addReviews, name='addReviews'),
    path('getReviews', views.getAllReviews, name='getReviews'),
    path('addvoucher', views.addVoucher, name='addvoucher'),
    path('getvoucher', views.getAllVouchers, name='getvoucher'),
    path('deletevoucher', views.deleteVoucer, name='deletevoucher'),
    path('getnewvoucher', views.getVoucher, name='getnewvoucher'),
    path('updatevoucher', views.updateVoucher, name='updatevoucher'),
    path('checkvoucher', views.checkVoucherValidity, name='checkvoucher'),
    path('savevoucherdata', views.saveVoucherData, name='savevoucherdata'),
    path('addcountry', views.addCountry, name='addcountry'),
    path('getallcountry',    getAllCountry.as_view(), name='getallcountry'),
    path('deletecountry',   views.deleteCountry, name='deletecountry'),
    path('getCityConfiguration',views.getCityConfiguration, name='getCityConfiguration'),
    path('updateCountryConfiguration/<int:pk>',updateCountryConfiguration.as_view(), name='updateCountryConfiguration'),
    path('getAllCity',   getAllCity.as_view(), name='getAllCity'),
    path('getcountries',  views.getallcountries, name='getallcountries'),
    path('addCity', views.addCity, name='addCity'),
    path('deleteCity', views.deleteCity, name='deleteCity'),
    path('getCountryConfiguration',views.getCountryConfiguration, name='getCityConfiguration'),
    path('updateCityConfiguration/<int:pk>',updateCityConfiguration.as_view(), name='updateCityConfiguration'),
    path('getwebcountries',  views.getWebsiteCountries, name='getwebcountries'),
    path('getwebcities',  views.getWebsiteCities, name='getwebcities'),
    path('addCustomerShipping',  views.addCustomerShipping, name='addCustomerShipping'),
    path('updatepayment',  views.updatePayment, name='updatepayment'),
    path('addcourier',  views.addCourier, name='addcourier'),
    path('getcourier',  views.getCourier, name='getcourier'),
    path('deletecourier',  views.deleteCourier, name='deletecourier'),
    path('getidcourier',  views.getIDCourier, name='getidcourier'),
    path('updatecourier',  views.updateCourier, name='updatecourier'),
    path('getAllCourierConfiguration', getAllCourierConfiguration.as_view(), name='getAllCourierConfiguration'),
    path('getAllCourier', getAllCourier.as_view(), name='getAllCourier'),
    path('addChargesConfiguration', views.addChargesConfiguration, name='addChargesConfiguration'),
    path('getChargesConfiguration', views.getChargesConfiguration, name='getChargesConfiguration'),
    path('updateChargesConfiguration/<int:pk>',updateChargesConfiguration.as_view(), name='updateChargesConfiguration'),
    path('calculateweight', views.calculateWeight, name='calculateweight'),






]