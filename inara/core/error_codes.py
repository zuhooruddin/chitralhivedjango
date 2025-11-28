SUCCESS	                        = 0
SUCCESS_MSG	                    = "SUCCESS"

ERROR                           = 1
ERROR_MSG                       = "ERROR"

NOT_EXIST                       = 404
NOT_EXIST_MSG                   = "Not Exist"

INTERNAL_SERVER_ERROR           = 500
INTERNAL_SERVER_ERROR_MSG       = "Internal Server Error"

ACCESS_TOKEN_BLACKLIST_MSG      = "Access token blacklisted Successfully"
ACCESS_TOKEN_NOT_BLACKLIST_MSG  = "Access token blacklist Failed"


#MANAGEMENT
ADD_MSG                         = "Added Successfully"
CREATE_MSG                      = "Created Successfully"
VIEW_MSG                        = "Viewed Successfully"
DELETE_MSG                      = "Deleted Successfully"
UPDATE_MSG                      = "Updated Successfully"
ACTIVATE_MSG                    = "Activated Successfully"
DEACTIVATE_MSG                  = "Deactivated Successfully"
APPROVE_MSG                     = "Approve Successfully"
DENY_MSG                        = "Deny Successfully"

NOT_ADD_MSG                     = "Not Added"
NOT_CREATE_MSG                  = "Not Created"
NOT_VIEW_MSG                    = "Not Viewed"
NOT_DELETE_MSG                  = "Not Deleted"
NOT_UPDATE_MSG                  = "Not Updated"
NOT_ACTIVATE_MSG                = "Not Activated Successfully"
NOT_DEACTIVATE_MSG              = "Not Deactivated Successfully"
NOT_APPROVE_MSG                 = "Not Approve Successfully"
NOT_DENY_MSG                    = "Not Deny Successfully"
NOT_SENT_TO_POS_MSG             = "Order not sent to POS! Kindly Contact Administrator"


ALREADY_EXIST                   = "Already Exist"

# LOGIN
LOGIN_REQ_MSG                   = "Please login to complete your request"
RSTRCTD_CALL_MSG                = "You are not authorized to perform this action"

AUTH_ACC_ERR_MSG                = "Something went wrong, Please try again!"
AUTH_ACC_NT_FND_MSG             = "This account does not exist"
AUTH_ACC_LCKD_MSG               = "You account is blocked, Please contact administrator!"
AUTH_DETLS_VRFD_MSG             = "Details verified successfully"
USR_LGIN_SUCCESS_MSG            = "Logged in successfully"
USR_LGIN_FAIL_MSG               = "Login failed, Please try again!"
USR_LGOUT_MSG                   = "Logout successful"
USR_LGOUT_ERR_MSG               = "Logout failed, Please try again"

#   ADMINS

EMAIL_ALREADY_EXIST             = "Email Already Exists"


# SCHOOL
SCHL_EXST_IN_BNDL_ERR_MSG       = "School is already associated with bundle. Kindly remove school from bundle to perform deletion."

# CATEGORY
CTGRY_EXST_IN_ITEM_ERR_MSG      = "Category is already associated with item. Kindly remove category from item to perform deletion."
CTGRY_EXST_IN_SQNC_ERR_MSG      = "Category is already associated with Section Sequence. Kindly remove category from item to perform deletion."
CTGRY_EXST_IN_BX_ORDR_ERR_MSG   = "Category is already associated with Individual Box Order. Kindly remove category from item to perform deletion."
CTGRY_FRM_POS_ERR_MSG           = "Category synced from POS cannot be deleted."

# CATEGORY ITEM
CTGRY_ITEM_UPDATE_SUCCESS_MSG   = "Category for items updated Successfully"
CTGRY_ITEM_NOT_UPDATE_ERR_MSG   = "Category for item not updated! Kindly Contact Administrator."

# Order
ORDR_NOTIFCTN_SEEN_SUCCESS_MSG  = "Notification Seen Updated Successfully"
ORDR_NOTIFCTN_SEEN_ERROR_MSG    = "Notification Seen Not Updated"

# Task Progress
CELERY_PROCESSING               = 700
CELERY_NO_TASK                  = 701
CELERY_ALRDY_TASK_IN_PROCESS    = 702
CELERY_ALRDY_COMPLETED          = 703
# CELERY_SUCCESS                  = 704

CELERY_EXCUTN_FAIL_MSG                  = "Synchronization failed. Kindly Contact Administrator"
CELERY_TSK_PRGRS_FAIL_MSG               = "Task Progress fetch failed. Kindly Contact Administrator"
CELERY_PROCESSING_CATEGORY_MSG          = "Category Synchronization task is being processed on server"
CELERY_PROCESSING_ITEM_MSG              = "Item Synchronization task is being processed on server"
CELERY_ALRDY_TASK_IN_PROGRESS_MSG       = "Task already in processing"
CELERY_NO_TSK_IN_PROGRESS_CATEGORY_MSG  = "Currently there is no Category Sync task in progress"
CELERY_NO_TSK_IN_PROGRESS_ITEM_MSG      = "Currently there is no Item Sync task in progress"
CELERY_TASK_STOP_SUCCESS_MSG            = "Synchronization Stopped Successfully"
CELERY_TASK_ALREADY_COMPLETED_MSG       = "Synchronization Already Completed"
CELERY_TASK_STOP_FAILED_MSG             = "Synchronization Stop Process Failed! Kindle Contact Administrator with relevant issue"



