from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(UserMaster)
admin.site.register(BlacklistedAccessToken)
admin.site.register(RoomManagement)


