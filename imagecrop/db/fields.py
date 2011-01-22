'''
Created on Jan 22, 2011

@author: arenner
'''
from django.db.models.fields.files import ImageField
from django.db import models

_crop_coords_field_name = lambda name: "%s_cropcoords" % name

class CroppedImageField (ImageField):
    
    description = "Stores an image and its cropping coordinates"
    
    def contribute_to_class(self,cls,name):
        crop_coords_field = models.CharField(max_length=30,
                                             editable=False,blank=True)
        
        cls.add_to_class(_crop_coords_field_name(name),crop_coords_field)
        
        super(CroppedImageField,self).contribute_to_class(cls,name)
        
from south.modelsinspector import add_introspection_rules
add_introspection_rules([],['^imagecrop\.db\.fields\.CroppedImageField'])