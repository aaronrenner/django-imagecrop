'''
Created on Feb 1, 2011

@author: arenner
'''
from django.contrib import admin
from testproject.testapp.models import TestImage
from imagecrop.forms.fields import CroppedImageField
from imagecrop.forms.widgets import CroppedImageFileInput

class TestImageAdmin(admin.ModelAdmin):
    formfield_overrides = {
        CroppedImageField: {'widget': CroppedImageFileInput},
    }


admin.site.register(TestImage, TestImageAdmin)