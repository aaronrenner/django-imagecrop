'''
Created on Jan 19, 2011

@author: arenner
'''
from django import forms
from imagecrop.forms.widgets import CroppedImageFileInput, \
    HiddenCroppedImageFileInput
from imagecrop.files import CroppedImageFile



class CroppedImageField(forms.ImageField):
    widget = CroppedImageFileInput 
    # This widget holds the initial value
    hidden_widget = HiddenCroppedImageFileInput
    
    def __init__(self, *args, **kwargs):
        

        super(CroppedImageField, self).__init__(*args, **kwargs)
        self._current_value=None
    
#    def prepare_value(self,value):
#        if isinstance(value,CroppedImageFile) and not value.name:
#            #return current_value, but update the crop coords
#            self._current_value.crop_coords=value.crop_coords
#            return self._current_value
#        return value
    
    def clean(self, value, initial):
        
        cleaned_file = super(CroppedImageField, self).clean(value, initial)
        #if value:
        cleaned_file.crop_coords = value.crop_coords
        #self._current_value=cleaned_file
        return cleaned_file
