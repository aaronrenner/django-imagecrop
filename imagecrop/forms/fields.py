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
    
    def __init__(self, image_width=None, image_height=None, *args, **kwargs):
        
        self._current_value = None
        self.image_width = image_width
        self.image_height = image_height
        super(CroppedImageField, self).__init__(*args, **kwargs)
        
    
    def prepare_value(self, value):
        if self._current_value and isinstance(value, CroppedImageFile) and not value.name:
            #return current_value, but update the crop coords
            self._current_value.crop_coords = value.crop_coords
            return self._current_value
        return value
    
    def clean(self, value, initial):
        
        cleaned_file = super(CroppedImageField, self).clean(value, initial)
        if cleaned_file:
            if value !=None and value.file == None:
                #Didn't upload a new file, so take the submitted crop coords
                cleaned_file.crop_coords = value.crop_coords
            else:
                #Uploaded a new file, so clear out the crop coords
                cleaned_file.crop_coords = None
            self._current_value = cleaned_file
        return cleaned_file
    
    def widget_attrs(self,widget):
        attrs={}
        if self.image_height and self.image_width:
            attrs['aspect_ratio']=float(self.image_width)/float(self.image_height)
        return attrs
