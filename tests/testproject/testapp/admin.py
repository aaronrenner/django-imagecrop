'''
Created on Feb 1, 2011

@author: arenner
'''
from django.contrib import admin
from django.forms.models import ModelForm
from imagecrop.forms.widgets import CroppedImageFileInput
from testproject.testapp.models import TestImage

class TestImageAdminForm(ModelForm):
    class Meta:
        model=TestImage
        widgets = {
            'image': CroppedImageFileInput(),
            'image_not_required': CroppedImageFileInput(),
        }

class TestImageAdmin(admin.ModelAdmin):
    form = TestImageAdminForm


admin.site.register(TestImage, TestImageAdmin)