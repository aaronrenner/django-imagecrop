'''
Created on Jan 19, 2011

@author: arenner
'''
from django.conf import settings
from django.contrib.admin.widgets import AdminFileWidget
from django.core.files.base import File
from django.core.files.images import ImageFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.forms.fields import FileField
from django.forms.widgets import Widget, HiddenInput, MultiWidget
from django.template import Template, Context
from django.utils.safestring import mark_safe
from imagecrop.files import CroppedImageFile, CropCoords
import os

class ImageCropCoordinatesInput(Widget):
    
    COORD_PARAMS = ["x1", "y1", "x2", "y2"]
    
    class Media:
        js = (
              "/static/imagecrop/js/jquery.min.js",
              "/static/imagecrop/js/jquery.Jcrop.min.js",
              )
        css = {
            'all':("/static/imagecrop/css/jquery.Jcrop.css",)
        }
    
    '''
    This widget allows the user to draw the crop rectangle and returns the upper left and
    lower right coordinates
    '''
    
    def __init__(self, attrs=None, aspect_ratio=0.0, crop_image_height=None, crop_image_width=None):
        '''
        Creates a new ImageCrop input
        
        attrs - HTML attributes
        crop_image_height - The max height of the image cropping control
        crop_image_width - The max width of the image cropping control
        '''
        
        self.aspect_ratio = aspect_ratio
        self.crop_image_height = crop_image_height
        self.crop_image_width = crop_image_width
        
        
        super(ImageCropCoordinatesInput, self).__init__(attrs)
        
        
    
    def render(self, name, value, attrs=None):
        """
        Code for rendering this widget
        
        name - Name of form field
        value - CroppedImageFile being cropped
        """
        
        if value is None:
            return ""
        
        if not isinstance(value, CroppedImageFile):
            raise ValueError("ImageCropCoordinatesInput requires a CroppedImageFile value")
        
        #Only display cropping control if the file has been saved to disk
        if isinstance(value.file, InMemoryUploadedFile) or not hasattr(value, 'url'):
            return ""
        
        output = []
        
        final_attrs = self.build_attrs(attrs)
        id_ = final_attrs.get('id', None)
        aspect_ratio = final_attrs.pop('aspect_ratio', 0.0)
        
        if not self.is_hidden:
            #Only render image cropping util if image_url has been set             
            t = Template('''
            <script language="Javascript">
                jQuery(window).load(function(){
                    function updateCoords(coords){
                        jQuery('#{{id}}_x1').val(coords.x);
                        jQuery('#{{id}}_y1').val(coords.y);
                        jQuery('#{{id}}_x2').val(coords.x2);
                        jQuery('#{{id}}_y2').val(coords.y2);
                    };
                    
                    
                    
                    var api = jQuery.Jcrop('#{{id}}',{
                        {%spaceless%}
                        {% if boxWidth %}
                        boxWidth:{{boxWidth}},
                        {%endif%}
                        {% if boxHeight %}
                        boxHeight:{{boxHeight}},
                        {%endif %}
                        {%endspaceless%}
                        aspectRatio: {{aspectRatio}},
                        onChange: updateCoords,
                        onSelect: updateCoords,
                        trueSize:[{{trueWidth}},{{trueHeight}}]
                    });
                    {% if coords %}
                    api.setSelect( [{{coords.x1}},{{coords.y1}},{{coords.x2}},{{coords.y2}}]);
                    {% endif %}
                });
                
                
                
            </script>
            <img src="{{imageurl}}" height="{{thumbnail_image.height}}" width="{{thumbnail_image.width}}" id='{{id}}' />
            ''')
            
            orig_thumbnail_path = os.path.join(settings.MEDIA_ROOT, value.orig_thumbnail_filename)
            
            if not os.path.exists(orig_thumbnail_path):
                value.generate_orig_thumbnail_file()
            
            thumbnail_image = ImageFile(open(orig_thumbnail_path))
            
            c = Context({
                   "id":id_,
                   "aspectRatio":aspect_ratio,
                   "imageurl": settings.MEDIA_URL + value.orig_thumbnail_filename,
                   "coords": value.crop_coords,
                   "boxWidth": self.crop_image_width,
                   "boxHeight":self.crop_image_height,
                   "trueWidth":value.width,
                   "trueHeight":value.height,
                   "thumbnail_image":thumbnail_image
                   })
            output.append(t.render(c))
           
        for param in ImageCropCoordinatesInput.COORD_PARAMS:
            widget = HiddenInput()
            
            if id_:
                final_attrs = dict(final_attrs, id='%s_%s' % (id_, param))
            coord = getattr(value.crop_coords, param) if value.crop_coords else None
            output.append(widget.render("%s_%s" % (name, param), coord, final_attrs))
            
        return mark_safe(u''.join(output))
    
    def value_from_datadict(self, data, files, name):
        # Returns a dictionary of the crop coordinates
        # Note: it does not return the CroppedImageFile that was passed to the render method
        result = CropCoords()
        
        valueFound = False
        
        for param in ImageCropCoordinatesInput.COORD_PARAMS:
            param_data = data.get(u"%s_%s" % (name, param,), None)
            if param_data:
                param_data = int(param_data)
            setattr(result, param, param_data)
            if getattr(result, param):
                valueFound = True
                
        if valueFound:
            return result
        else: return None
        
        

class CroppedImageFileInput(MultiWidget, FileField):
    """
    Complete file upload with image cropper widget
    """
    
    def __init__(self, attrs=None):
        
        aspect_ratio = attrs.get('apsect_ratio', 0.0) if attrs else 0.0
        
        widgets = (AdminFileWidget(attrs=attrs),
                   ImageCropCoordinatesInput(attrs=attrs, aspect_ratio=aspect_ratio),
                   )
        super(CroppedImageFileInput, self).__init__(widgets, attrs)
     
    def decompress(self, value):
        if isinstance(value, CroppedImageFile):
            return [value, value]
        return [None, None]
    
    def value_from_datadict(self, data, files, name):
        
        values = super(CroppedImageFileInput, self).value_from_datadict(data, files, name)
        if isinstance(values[0], File):
            file = CroppedImageFile(values[0])
        else:
            file = CroppedImageFile(None)
            #return None
        file.crop_coords = values[1]
        return file
     
    def _has_changed(self, initial, data):
        if data.file:
            # file changed
            return True
        return initial.crop_coords != data.crop_coords
    
class HiddenCroppedImageFileInput(CroppedImageFileInput):
    """
    Splits the cropped image file input into two hidden inputs
    """
    def __init__(self, attrs=None):
        super(HiddenCroppedImageFileInput, self).__init__(attrs)
        
        self.widgets = (HiddenInput(attrs=attrs),
                   ImageCropCoordinatesInput(attrs=attrs),
                   ) 

        
        for widget in self.widgets:
            widget.input_type = 'hidden'
            widget.is_hidden = True   
            
#    def render(self, name, value, attrs=None):
#        self.initial_value=value
#        return super(HiddenCroppedImageFileInput,self).render(name,value,attrs) 
