'''
Created on Jan 19, 2011

@author: arenner
'''
from django import forms
from imagecrop.forms.widgets import ImageCropCoordinatesInput
from django.core import validators
from django.forms.fields import MultiValueField, ImageField
from imagecrop.files import CroppedImageFile



class ImageCropCoordinatesField(forms.Field):
    '''
    This field holds the cropping coordinates for an image
    '''
    
    widget = ImageCropCoordinatesInput
    
    def __init__(self,*args,**kwargs):
        
        super(ImageCropCoordinatesField,self).__init__(*args,**kwargs)
        
    def to_python(self,value):
        
        if value in validators.EMPTY_VALUES:
            return None
        return value

class CroppedImageField(MultiValueField):
    
    def __init__(self, *args, **kwargs):
        
        fields = (
            ImageField(*args,**kwargs),
            ImageCropCoordinatesField(*args,**kwargs),
        )
        
        super(CroppedImageField,super).__init__(fields, *args, **kwargs)
        
    def compress(self,data_list):
        if data_list:
            return CroppedImageFile(data_list[0], crop_coords=data_list[1])
        return None
        
    #def clean(self, value):
    #    """
    #    Validates the given value and returns its "cleaned" value as an
    #    appropriate Python object.
    #    
    #    Raises ValidationError for any errors.
    #    """
    #    value = self.to_python(value)
    #    self.validate(value)
    #    self.run_validators(value)
    #    return value
    
    
    #def compress(self,data_list):
    #    if data_list:
    #        return data_list
    #    return None