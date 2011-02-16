'''
Created on Jan 22, 2011

@author: arenner
'''
from django.conf import settings
from django.db import models
from django.db.models import signals
from django.db.models.fields.files import FileDescriptor, FieldFile
from imagecrop.files import CroppedImageFile, decode_crop_coord, \
    CropCoordEncoder, CropCoords
from imagecrop.forms import fields
import os
import json
import Image



class CroppedImageFieldFile(FieldFile, CroppedImageFile):
    """
    The CroppedImageFile, but has the required FieldFile attributes
    """
    
    
    def _get_meta_filename(self):
        '''
        Gets the filename containing the crop coordinates
        '''
        if self.name:
            return os.path.join(settings.MEDIA_ROOT, self.name + ".meta")
        return None  
    
    meta_filename = property(_get_meta_filename)
    
    def _get_cropped_filename(self):
        '''
        Gets the filename for the cropped file
        '''
        if self.name:
            filename_parts = os.path.splitext(self.name)
            return "%s.cropped%s" % (filename_parts[0], filename_parts[1])
        return None
    
    cropped_filename = property(_get_cropped_filename)
    
    def _get_cropped_thumbnail_filename(self):
        '''
        Gets the filename for the cropped file
        '''
        if self.name:
            filename_parts = os.path.splitext(self.name)
            return "%s.thumb-cropped%s" % (filename_parts[0], filename_parts[1])
        return None
    
    cropped_thumbnail_filename = property(_get_cropped_thumbnail_filename)
    
    def _get_orig_thumbnail_filename(self):
        '''
        Gets the thumbnail of the original image that is used for the
        cropping control
        '''
        if self.name:
            filename_parts = os.path.splitext(self.name)
            return "%s.origthumb%s" % (filename_parts[0], filename_parts[1])
        return None
        
    orig_thumbnail_filename = property(_get_orig_thumbnail_filename)
    
    def generate_orig_thumbnail_file(self):
        '''
        Generates a thumbnail of the original file
        '''
        
        #generate original thumbnail
        if self.name:
            baseimage = Image.open(os.path.join(settings.MEDIA_ROOT, self.name), 'r')
            thumbsize = (getattr(settings, "ORIG_THUMBNAIL_HEIGHT", CroppedImageField.DEFAULT_ORIG_THUMBNAIL_HEIGHT),
                         getattr(settings, "ORIG_THUMBNAIL_WIDTH", CroppedImageField.DEFAULT_ORIG_THUMBNAIL_WIDTH))
            baseimage.thumbnail(thumbsize, Image.ANTIALIAS)
            thumbnail_orig_filename = os.path.join(settings.MEDIA_ROOT, self.orig_thumbnail_filename)
            baseimage.save(thumbnail_orig_filename)
            
    def generate_cropped_thumbnail_file(self):
        '''
        Generates a thumbnail of the cropped file
        '''
        
        cropped_file_path= os.path.join(settings.MEDIA_ROOT,self.cropped_filename)
        
        #generate original thumbnail
        if self.cropped_filename and os.path.exists(cropped_file_path):
            baseimage = Image.open(cropped_file_path, 'r')
            thumbsize = (getattr(settings, "CROP_THUMBNAIL_HEIGHT", CroppedImageField.DEFAULT_CROPPED_THUMBNAIL_HEIGHT),
                         getattr(settings, "CROP_THUMBNAIL_WIDTH", CroppedImageField.DEFAULT_CROPPED_THUMBNAIL_WIDTH))
            baseimage.thumbnail(thumbsize, Image.ANTIALIAS)
            thumbnail_cropped_filename = os.path.join(settings.MEDIA_ROOT, self.cropped_thumbnail_filename)
            baseimage.save(thumbnail_cropped_filename)
            
    def apply_default_cropping(self, image_width=None, image_height=None):
        '''
        Sets cropcoords to default values
        
        Desired image width and image height
        '''
        if not self.name:
            return
        
        if image_width and image_height:
            desired_aspect_ratio = float(image_width) / float(image_height) 
            image_aspect_ratio = float(self.width) / float(self.height)
            
            
            if image_aspect_ratio >= 1:
                #Landscape
                crop_width = self.height 
                crop_height = int(self.height / desired_aspect_ratio)
            else:
                #Portrait
                crop_width = int(self.width / desired_aspect_ratio)
                crop_height = self.width 
                
            #calculate offset
            x_offset = (self.width - crop_width) / 2
            y_offset = (self.height - crop_height) / 2
            
            
            self.crop_coords = CropCoords(x1=x_offset, y1=y_offset, x2=crop_width + x_offset, y2=crop_height + y_offset)
            
        else:
            self.crop_coords = CropCoords(0, 0, self.height, self.width)
        

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
        
        if not orig_val:
            return None
        
        # Have the super class take care of most of the dirty work
        fieldfile = super(CroppedImageFileDescriptor, self).__get__(instance, owner)
        
        # Now set up the crop coords
        # If a CroppedImageFile needs to be converted to a CroppedImageFieldFile
        if isinstance(orig_val, CroppedImageFile) and not isinstance(orig_val, CroppedImageFieldFile):
            fieldfile.crop_coords = fieldfile.file.crop_coords
        
        #Most likely loaded from the db, so check for crop file
        if isinstance(orig_val, basestring):
            # Look for crop_coords
            try:
                cropfile = fieldfile.meta_filename
                if os.path.exists(cropfile):
                    result = json.load(open(cropfile, 'r'), object_hook=decode_crop_coord)
                    fieldfile.crop_coords = result['crop']
            except:
                pass
        
        # Store filefield for future  
        instance.__dict__[self.field.name] = fieldfile
        
        return fieldfile
    
    def __set__(self, instance, value):
        super(CroppedImageFileDescriptor, self).__set__(instance, value)
        
        

class CroppedImageField (models.FileField):
    
    DEFAULT_ORIG_THUMBNAIL_HEIGHT = 600
    DEFAULT_ORIG_THUMBNAIL_WIDTH = 600
    DEFAULT_CROPPED_THUMBNAIL_HEIGHT = 150
    DEFAULT_CROPPED_THUMBNAIL_WIDTH = 150
    
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
        
    def pre_save(self, model_instance, add):
        file = super(CroppedImageField, self).pre_save(model_instance, add)
        
        if file.crop_coords == None:
            file.apply_default_cropping(image_width = self.image_width,image_height=self.image_height)
        
        if file:
            meta_filename = file.meta_filename
            if meta_filename:
                f = open(meta_filename, 'w')
                f.write(json.dumps({'crop':file.crop_coords}, cls=CropCoordEncoder))
                f.close()
        
        return file
    
    
        
    def contribute_to_class(self, cls, name):
        super(CroppedImageField, self).contribute_to_class(cls, name)
        
        signals.post_save.connect(self._crop_image, sender=cls)
        signals.pre_delete.connect(self._cleanup_files, sender=cls)
     
    def _cleanup_files(self, instance, sender, **kwargs):
        field = getattr(instance, self.attname)
        
        if field:
            meta_filename = field.meta_filename
            if meta_filename and os.path.exists(meta_filename):
                os.remove(meta_filename)
                
            cropped_filename = os.path.join(settings.MEDIA_ROOT, field.cropped_filename)
            if cropped_filename and os.path.exists(cropped_filename):
                os.remove(cropped_filename)
      
    def _crop_image(self, sender, instance, **kwargs):
        '''
        Generates cropped and resized images needed for control to work
        '''
        field = getattr(instance, self.attname)
        
        if field and field.file:
            filename = field.file.name;
            
            #generate original thumbnail
            field.generate_orig_thumbnail_file()
            
            #Generate cropped image 
            if field.crop_coords != None:
                filename = field.file.name;
                crop_coords = field.crop_coords
                
                #Crop the image
                baseimage = Image.open(filename, 'r')
                cropped_image = baseimage.crop((crop_coords.x1, crop_coords.y1, crop_coords.x2, crop_coords.y2))
                if self.image_height and self.image_width:
                    cropped_image = cropped_image.resize((self.image_width, self.image_height), Image.ANTIALIAS)
                
                cropped_image.load()
                
                #Save the cropped image
                cropped_filename = os.path.join(settings.MEDIA_ROOT, field.cropped_filename)
                cropped_image.save(cropped_filename)
                
            #Generate Thumbnail of cropped image
            field.generate_cropped_thumbnail_file()
        
            
            
    
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
