'''
Created on Jan 22, 2011

@author: arenner
'''
from django.db import models
import json
from south.modelsinspector import add_introspection_rules
from imagecrop.forms import fields
from django.db.models.fields.files import FileDescriptor, FieldFile
from imagecrop.files import CroppedImageFile



class CroppedImageFieldFile(FieldFile,CroppedImageFile):
    """
    The CroppedImageFile, but has the required FieldFile attributes
    """
    pass

class CroppedImageFileDescriptor(FileDescriptor):
    '''
    The descriptor for the file attribute on the model instance. Returns a
        FieldFile when accessed so you can do stuff like::
    
            >>> instance.file.size
    
        Assigns a file object on assignment so you can do::
    
            >>> instance.file = File(...)
    '''
    def __get__(self, instance=None, owner=None):
        if instance is None:
                raise AttributeError(
                    "The '%s' attribute can only be accessed from %s instances."
                    % (self.field.name, owner.__name__))
        
        # The instance dict contains whatever was originally assigned
        # in __set__.
        value = instance.__dict__[self.field.name]
        
        
        
        # if it's a CroppedImageFieldFile, it's good to go
        if isinstance(value, CroppedImageFieldFile):
            return value 
        
        # Holds eventual crop coordinates
        crop_coords = None
        # If it's a CroppedImageFile, extract the crop_coords and let the superclass
        # convert it to a CroppedImageFileField. We will assign the crop_coords later
        if isinstance(value, CroppedImageFieldFile):
            crop_coords = value.crop_coords
        
        #try to decode json string
        if isinstance(value, basestring):
            #Eventual holder of filename
            filename=None
            try:
                valuedic = json.loads(value)
                filename = valuedic.get('filename',None)
                crop_coords = valuedic.get('crop_coords',None)
            except ValueError:
                # Not json, so must be a filename
                filename = value
            
            # If the filename is available from a dictionary, run set, so the superclass
            # can do the correct conversions
            if filename:
                self.__set__(instance,filename)  
        
        #Handle File values, filename strings
        superval = super(CroppedImageFileDescriptor,self).__get__(instance,owner)
        
        # Set the crop coords
        superval.crop_coords = crop_coords
        
        return superval
        
        

class CroppedImageField (models.FileField):
    
    attr_class = CroppedImageFieldFile
    
    descriptor_class= CroppedImageFileDescriptor
    
    #__metaclass__ = models.SubfieldBase
    
    description = "Stores an image and its cropping coordinates"
    
    def __init__(self,image_width=None,image_height=None,**kwargs):
        '''
        Constructor for CroppedImageField
        
        image_width - The desired width of the cropped image.
        image_height - The desired height of the cropped image.
        '''
        
        self.image_width=kwargs.pop('image_width',None)
        self.image_height=kwargs.pop('image_height',None)
        
        #Setting default max_length
        kwargs['max_length'] = kwargs.get('max_length', 250)
        
        super(CroppedImageField,self).__init__(**kwargs)
        
    def get_prep_value(self, value):
        if value is None:
            return None
        
        result = {
                  u'filename': super(CroppedImageField,self).get_prep_value(value),
                  u'crop_coords': value.crop_coords,
                }
        return json.dumps(result)
    
    def formfield(self, **kwargs):
        defaults = {'form_class': fields.CroppedImageField}
        defaults.update(kwargs)
        return super(CroppedImageField,self).formfield(**defaults)
    
    #def to_python(self,value):
    #    return value
#        if value is None or value == "":
#            return None
#        if isinstance(value,CroppedImageFieldFile):
#            return value
#        #Value is string coming form database
#        myjson = json.loads(value)
#        return myjson
    
#    def contribute_to_class(self,cls,name):
#        crop_coords_field = CoordinatesField(max_length=50,
#                                             editable=False,blank=True)
#        
#        cls.add_to_class(_crop_coords_field_name(name),crop_coords_field)
#        
#        super(CroppedImageField,self).contribute_to_class(cls,name)
        

add_introspection_rules([
     ( 
        [CroppedImageField], # Class(es) these apply to
        [], # Positional arguments(not used)
        {
            "image_width": ["image_width", {"default": None}],
            "image_height": ["image_height", {"default": None}],
        },
     ),

],['^imagecrop\.db\.fields\.CroppedImageField'])