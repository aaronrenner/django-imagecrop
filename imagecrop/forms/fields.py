'''
Created on Jan 19, 2011

@author: arenner
'''
from django import forms
from imagecrop.forms.widgets import ImageCropCoordinatesInput,\
    CroppedImageFileInput
from django.core import validators
from imagecrop.files import CroppedImageFile



class ImageCropCoordinatesField(forms.Field):
    '''
    This field holds the cropping coordinates for an image
    '''
    
    widget = ImageCropCoordinatesInput
    
#    def __init__(self,*args,**kwargs):
#        
#        super(ImageCropCoordinatesField,self).__init__(*args,**kwargs)
        
    def to_python(self,value):
        
        if value in validators.EMPTY_VALUES:
            return None
        return value

class CroppedImageField(forms.MultiValueField):
    
    widget = CroppedImageFileInput
    
    def __init__(self, *args, **kwargs):
        
        fields = (
            
            forms.ImageField(*args,**kwargs),
            forms.CharField(*args,**kwargs),
            
            #ImageCropCoordinatesField(),
        )
        
        #removing max_length argument so the Field class doesn't error out
        self.max_length = kwargs.pop('max_length', None)
        
        super(CroppedImageField,self).__init__(fields,*args, **kwargs)
        
    def compress(self,data_list):
        if data_list:
            #Test to see if a file was uploaded
            return data_list
#            if (data_list[0]):
#                file = CroppedImageFile(data_list[0].name, crop_coords=data_list[1])
#                return file  
        return None
        
    def clean(self, value):
        print "Clean"
        super(CroppedImageField,self).clean(value)
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