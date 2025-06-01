from django.contrib import admin
from .models import PasswordResetRequest, AdminNotification
class PasswordResetRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'request_time', 'is_reset_allowed']

class AdminNotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'created_at']

admin.site.register(PasswordResetRequest, PasswordResetRequestAdmin)
admin.site.register(AdminNotification, AdminNotificationAdmin)
from django.contrib import admin
from .models import *

class BatchMasterAdmin(admin.ModelAdmin):
    list_display = ('batchNo', 'batchId')
    search_fields = ('batchNo',)

class SemesterMasterAdmin(admin.ModelAdmin):
    list_display = ('semester', 'semesterId')
    search_fields = ('semester',)

class StudentMasterAdmin(admin.ModelAdmin):
    list_display = ('studentName', 'studentRegNo', 'studentEmail', 'studentMobile')
    search_fields = ('studentName', 'studentRegNo', 'studentEmail')
##################################################################

from django.contrib import admin
from .models import TransactionMaster

admin.site.register(TransactionMaster)

from django.contrib import admin
from .models import CertificateMaster

@admin.register(CertificateMaster)
class CertificateMasterAdmin(admin.ModelAdmin):
    # Fields to display in the admin list view
    list_display = ('student', 'certificateType', 'issueDate', 'status')
    
    # Fields to enable searching
    search_fields = ('student__studentName', 'certificateType', 'status')

    # Fields for filtering
    list_filter = ('status', 'issueDate', 'certificateType')
