'''
Created on Jan 19, 2011

@author: arenner
'''
from django import forms
from imagecrop.forms.widgets import CroppedImageFileInput, \
    HiddenCroppedImageFileInput



class CroppedImageField(forms.ImageField):
    widget = CroppedImageFileInput 
    # This widget holds the initial value
    hidden_widget = HiddenCroppedImageFileInput
    
    def __init__(self, *args, **kwargs):
        

        super(CroppedImageField, self).__init__(*args, **kwargs)
        
    
    def clean(self, value, initial):
        
        cleaned_file = super(CroppedImageField, self).clean(value, initial)
        cleaned_file.crop_coords = value.crop_coords
        return cleaned_file
