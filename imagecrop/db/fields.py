'''
Created on Jan 22, 2011

@author: arenner
'''
from django.db import models
from django.db.models.fields.files import FileDescriptor, FieldFile
from imagecrop.files import CroppedImageFile, decode_crop_coord,\
    CropCoordEncoder
from imagecrop.forms import fields
from django.db.models import signals
import os,json,Image
from django.conf import settings



class CroppedImageFieldFile(FieldFile, CroppedImageFile):
    """
    The CroppedImageFile, but has the required FieldFile attributes
    """
    
    
    def _get_meta_filename(self):
        '''
        Gets the filename containing the crop coordinates
        '''
        if self.name:
            return os.path.join(settings.MEDIA_ROOT,self.name +".meta")
        return None  
    
    meta_filename=property(_get_meta_filename)
    
    def _get_cropped_filename(self):
        '''
        Gets the filename for the cropped file
        '''
        if self.name:
            filename_parts = os.path.splitext(self.name)
            return "%s.cropped%s" % (filename_parts[0],filename_parts[1])
        return None
    
    cropped_filename = property(_get_cropped_filename)

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
                cropfile = fieldfile.meta_filename
                if os.path.exists(cropfile):
                    result = json.load(open(cropfile,'r'),object_hook=decode_crop_coord)
                    fieldfile.crop_coords = result['crop']
            except:
                pass
        
        # Store filefield for future  
        instance.__dict__[self.field.name]=fieldfile
        
        return fieldfile
    
    def __set__(self, instance, value):
        super(CroppedImageFileDescriptor, self).__set__(instance, value)
        
        

class CroppedImageField (models.FileField):
    
    attr_class = CroppedImageFieldFile
    
    descriptor_class = CroppedImageFileDescriptor
    
    description = "Stores an image and its cropping coordinates"
    
    def __init__(self, image_width=None, image_height=None, **kwargs):
        '''
        Constructor for CroppedImageField
        
        image_width - The desired width of the cropped image.
        image_height - The desired height of the cropped image.
        '''
        
        self.image_width = image_width
        self.image_height = image_height
        
        super(CroppedImageField, self).__init__(**kwargs)
        
    def pre_save(self,model_instance,add):
        file = super(CroppedImageField, self).pre_save(model_instance,add)
        
        meta_filename = file.meta_filename
        if meta_filename:
            f = open(meta_filename,'w')
            f.write(json.dumps({'crop':file.crop_coords},cls=CropCoordEncoder))
            f.close()
        
        return file
    
    
        
    def contribute_to_class(self, cls, name):
        super(CroppedImageField, self).contribute_to_class(cls,name)
        
        signals.post_save.connect(self._crop_image,sender=cls)
        signals.pre_delete.connect(self._cleanup_files, sender=cls)
     
    def _cleanup_files(self, instance, sender, **kwargs):
        field = getattr(instance, self.attname)
        
        meta_filename = field.meta_filename
        if meta_filename and os.path.exists(meta_filename):
            os.remove(meta_filename)
            
        cropped_filename = os.path.join(settings.MEDIA_ROOT,field.cropped_filename)
        if cropped_filename and os.path.exists(cropped_filename):
            os.remove(cropped_filename)
      
    def _crop_image(self,sender,instance,**kwargs):
        field = getattr(instance, self.attname)
        
        if field.file and field.crop_coords !=None:
            filename = field.file.name;
            crop_coords = field.crop_coords
            
            #Crop the image
            baseimage = Image.open(filename, 'r')
            cropped_image = baseimage.crop((crop_coords.x1, crop_coords.y1, crop_coords.x2, crop_coords.y2))
            if self.image_height and self.image_width:
                cropped_image = cropped_image.resize((self.image_width,self.image_height),Image.ANTIALIAS)
            
            cropped_image.load()
            
            #Save the cropped image
            cropped_filename = os.path.join(settings.MEDIA_ROOT,field.cropped_filename)
            cropped_image.save(cropped_filename)
            
    
    def formfield(self, **kwargs):
        defaults = {
                    'form_class': fields.CroppedImageField,
                    'show_hidden_initial':True,
                    'image_height':self.image_height,
                    'image_width': self.image_width,
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
