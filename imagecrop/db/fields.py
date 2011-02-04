'''
Created on Jan 22, 2011

@author: arenner
'''
from django.db import models
from django.db.models.fields.files import FileDescriptor, FieldFile
from imagecrop.files import CroppedImageFile
from imagecrop.forms import fields
from django.db.models import signals
import os,json
from django.conf import settings



class CroppedImageFieldFile(FieldFile, CroppedImageFile):
    """
    The CroppedImageFile, but has the required FieldFile attributes
    """
#    def __init__(self,instance,field,name):
#        super(FieldFile, self).__init(instance,field,name)
    
    
    def get_crop_filename(self):
        '''
        Gets the filename containing the crop coordinates
        '''
        return os.path.join(settings.MEDIA_ROOT,os.path.splitext(self.name)[0] +".crop")   

class CroppedImageFileDescriptor(FileDescriptor):
    '''
    The descriptor for the file attribute on the model instance. Returns a
        FieldFile when accessed so you can do stuff like::
    
            >>> instance.file.size
    
        Assigns a file object on assignment so you can do::
    
            >>> instance.file = File(...)
    '''
    def __get__(self, instance=None, owner=None):
        
        # The instance dict contains whatever was originally assigned
        # in __set__.
        orig_val = instance.__dict__[self.field.name]
        
        # Have the super class take care of most of the dirty work
        fieldfile = super(CroppedImageFileDescriptor, self).__get__(instance, owner)
        
        # Now set up the crop coords
        # If a CroppedImageFile needs to be converted to a CroppedImageFieldFile
        if isinstance(orig_val,CroppedImageFile) and not isinstance(orig_val,CroppedImageFieldFile):
            fieldfile.crop_coords = fieldfile.file.crop_coords
        
        #Most likely loaded from the db, so check for crop file
        if isinstance(orig_val, basestring):
            # Look for crop_coords
            try:
                cropfile = fieldfile.get_crop_filename()
                if os.path.exists(cropfile):
                    result = json.load(open(cropfile,'r'))
                    fieldfile.crop_coords = result['crop']
            except:
                pass
        
        # Store filefield for future  
        instance.__dict__[self.field.name]=fieldfile
        
        return fieldfile
        
#        if instance is None:
#                raise AttributeError(
#                    "The '%s' attribute can only be accessed from %s instances."
#                    % (self.field.name, owner.__name__))
#        
#        
#        
#        
#        
#        
#        # if it's a CroppedImageFieldFile, it's good to go
#        if isinstance(value, CroppedImageFieldFile):
#            return value 
#        
#        # Holds eventual crop coordinates
#        crop_coords = None
#        # If it's a CroppedImageFile, extract the crop_coords and let the superclass
#        # convert it to a CroppedImageFileField. We will assign the crop_coords later
#        if isinstance(value, CroppedImageFieldFile):
#            crop_coords = value.crop_coords
#        
#        #try to decode json string
#        if isinstance(value, basestring):
#            #Eventual holder of filename
#            filename = None
#            try:
#                valuedic = json.loads(value)
#                filename = valuedic.get('filename', None)
#                crop_coords = valuedic.get('crop_coords', None)
#            except ValueError:
#                # Not json, so must be a filename
#                filename = value
#            
#            # If the filename is available from a dictionary, run set, so the superclass
#            # can do the correct conversions
#            if filename:
#                self.__set__(instance, filename)  
#        
#        #Handle File values, filename strings
#        superval = super(CroppedImageFileDescriptor, self).__get__(instance, owner)
#        
#        # Set the crop coords
#        superval.crop_coords = crop_coords
#        
#        return superval
    
    def __set__(self, instance, value):
        super(CroppedImageFileDescriptor, self).__set__(instance, value)
        
        

class CroppedImageField (models.FileField):
    
    #__metaclass__ = models.SubfieldBase
    
    attr_class = CroppedImageFieldFile
    
    descriptor_class = CroppedImageFileDescriptor
    
    description = "Stores an image and its cropping coordinates"
    
    def __init__(self, image_width=None, image_height=None, **kwargs):
        '''
        Constructor for CroppedImageField
        
        image_width - The desired width of the cropped image.
        image_height - The desired height of the cropped image.
        '''
        
        self.image_width = image_height
        self.image_height = image_width
        
        super(CroppedImageField, self).__init__(**kwargs)
        
    def pre_save(self,model_instance,add):
        file = super(CroppedImageField, self).pre_save(model_instance,add)
        
        f = open(file.get_crop_filename(),'w')
        f.write(json.dumps({'crop':file.crop_coords}))
        f.close()
        
        return file
        
    def contribute_to_class(self, cls, name):
        super(CroppedImageField, self).contribute_to_class(cls,name)
        
        # Attach update cropcoords
#        signals.post_init.connect(self.update_crop_coords, sender=cls)
        
#    def update_crop_coords(self,instance,force=False, *args, **kwargs):
#        
#        file = getattr(instance, self.attname)
#        print instance
        
#    def get_prep_value(self, value):
#        if value is None:
#            return None
#        
#        filename = super(CroppedImageField, self).get_prep_value(value)
#        
#        result = {
#                  u'filename': filename,
#                  u'crop_coords': value.crop_coords,
#                }
#        return json.dumps(result)
    
    def formfield(self, **kwargs):
        defaults = {
                    'form_class': fields.CroppedImageField,
                    'show_hidden_initial':True,
            }
        defaults.update(kwargs)
        return super(CroppedImageField, self).formfield(**defaults)
        
#South Specific.
try:
    from south.modelsinspector import add_introspection_rules
    
    add_introspection_rules([
         (
            [CroppedImageField], # Class(es) these apply to
            [], # Positional arguments(not used)
            {
                "image_width": ["image_width", {"default": None}],
                "image_height": ["image_height", {"default": None}],
            },
         ),
    
    ], ['^imagecrop\.db\.fields\.CroppedImageField'])
except ImportError:
    #south is not installed
    pass
