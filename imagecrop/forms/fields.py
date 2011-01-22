'''
Created on Jan 19, 2011

@author: arenner
'''
from django import forms
from imagecrop.forms.widgets import ImageCropCoordinatesInput
from django.core import validators



class ImageCropCoordinatesField(forms.Field):
    '''
    This field holds the cropping coordinates for an image
    '''
    
    widget = ImageCropCoordinatesInput('/static/flowers.jpg',aspect_ratio=(950.0/280.0),crop_image_height='400')
    
    def __init__(self,*args,**kwargs):
        #fields= (
        #    IntegerField(),
        #    IntegerField(),
        #    IntegerField(),
        #    IntegerField(),    
        #)
        
        super(ImageCropCoordinatesField,self).__init__(*args,**kwargs)
        
    def to_python(self,value):
        
        if value in validators.EMPTY_VALUES:
            return None
        return value
        
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