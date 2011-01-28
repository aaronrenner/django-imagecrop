'''
Created on Jan 19, 2011

@author: arenner
'''
from django import forms
from imagecrop.forms.widgets import ImageCropCoordinatesInput,\
    CroppedImageFileInput, HiddenCroppedImageFileInput
from django.core import validators
from imagecrop.files import CroppedImageFile
from django.core.exceptions import ValidationError



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

class CroppedImageField(forms.ImageField):
    
    widget = CroppedImageFileInput
    # This widget holds the initial value
    hidden_widget = HiddenCroppedImageFileInput
    
    def __init__(self, *args, **kwargs):
        
#        fields = (
#            
#            forms.ImageField(*args,**kwargs),
#            forms.CharField(*args,**kwargs),
#            
#            #ImageCropCoordinatesField(),
#        )
        
        #removing max_length argument so the Field class doesn't error out
        #self.max_length = kwargs.pop('max_length', None)
        
        super(CroppedImageField,self).__init__(*args, **kwargs)
        
#    def to_python(self,data):
#        f = super(CroppedImageField,self).to_python(data)
#        return f
    
    def clean(self,value,initial):
        
        cleaned_file=super(CroppedImageField,self).clean(value,initial)
#        if value.file:
#            cleaned_file = value.file
#        else:
#            cleaned_file = initial.file
        cleaned_file.crop_coords=value.crop_coords
        #return 
        return cleaned_file
    
#    def compress(self,data_list):
#        if data_list:
#            #Test to see if a file was uploaded
#            return data_list
##            if (data_list[0]):
##                file = CroppedImageFile(data_list[0].name, crop_coords=data_list[1])
##                return file  
#        return None
        
#    def clean(self, value):
#        print "Clean"
#        super(CroppedImageField,self).clean(value)
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