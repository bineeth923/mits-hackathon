from django.contrib import admin

# Register your models here.
from bloodfinder.models import SMSBuffer, Donor

admin.site.register(SMSBuffer)
admin.site.register(Donor)