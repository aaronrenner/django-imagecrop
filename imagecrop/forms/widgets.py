'''
Created on Jan 19, 2011

@author: arenner
'''
from django.forms.widgets import Widget, HiddenInput, MultiWidget, FileInput,\
    Media, TextInput
from django.template import Template, Context
from django.utils.safestring import mark_safe 
from imagecrop.files import CroppedImageFile
from django.core.files.base import File
from django.contrib.admin.widgets import AdminFileWidget
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.forms.fields import FileField

class ImageCropCoordinatesInput(Widget):
    
    COORD_PARAMS= ["x1","y1","x2","y2"]
    
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
    
    def __init__(self,attrs=None,aspect_ratio=0.0, crop_image_height=None, crop_image_width=None):
        '''
        Creates a new ImageCrop input
        
        attrs - HTML attributes
        aspect_ratio - width/height. 0 for N/A. 1.0 for square
        crop_image_height - The max height of the image cropping control
        crop_image_width - The max width of the image cropping control
        '''
        super(ImageCropCoordinatesInput,self).__init__(attrs)
        
        self.aspect_ratio=aspect_ratio
        self.crop_image_height = crop_image_height
        self.crop_image_width = crop_image_width
        
    
    def render(self, name, value, attrs=None):
        """
        Code for rendering this widget
        
        name - Name of form field
        value - CroppedImageFile being cropped
        """
        
        if value is None:
            return ""
        
        if not isinstance(value,CroppedImageFile):
            raise ValueError("ImageCropCoordinatesInput requires a CroppedImageFile value")
        
        #Only display cropping control if the file has been saved to disk
        if isinstance(value.file,InMemoryUploadedFile):
            return ""
        
        output = []
        
        final_attrs = self.build_attrs(attrs)
        id_ = final_attrs.get('id', None)
        
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
                    
                    
                    
                    jQuery('#{{id}}').Jcrop({
                        {%spaceless%}
                        {% if coords.items|length == 4 %}
                        setSelect: [{{coords.x1}},{{coords.y1}},{{coords.x2}},{{coords.y2}}],
                        {% endif %}
                        {% if boxWidth %}
                        boxWidth:{{boxWidth}},
                        {%endif%}
                        {% if boxHeight %}
                        boxHeight:{{boxHeight}},
                        {%endif %}
                        {%endspaceless%}
                        aspectRatio: {{aspectRatio}},
                        onChange: updateCoords,
                        onSelect: updateCoords
                    });
                });
                
                
                
            </script>
            <img src="{{imageurl}}" id='{{id}}' />
            ''')
            
            c = Context({
                   "id":id_,
                   "aspectRatio":self.aspect_ratio,
                   "imageurl": value.url,
                   "coords": value.crop_coords,
                   "boxWidth": self.crop_image_width,
                   "boxHeight":self.crop_image_height,
                   })
            output.append(t.render(c))
           
        for param in ImageCropCoordinatesInput.COORD_PARAMS:
            widget = HiddenInput()
            
            if id_:
                final_attrs = dict(final_attrs,id='%s_%s' % (id_, param))
            coord = value.crop_coords.get(param,None) if value.crop_coords else None
            output.append(widget.render("%s_%s" % (name,param),coord,final_attrs))
            
        return mark_safe(u''.join(output))
    
    def value_from_datadict(self, data, files, name):
        # Returns a dictionary of the crop coordinates
        # Note: it does not return the CroppedImageFile that was passed to the render method
        result = {}
        
        valueFound=False
        
        for param in ImageCropCoordinatesInput.COORD_PARAMS:
            result[param]= data.get(u"%s_%s" % (name,param,),None)
            if result[param]:
                valueFound=True
                
        if valueFound:
            return result
        else: return None
        
        

class CroppedImageFileInput(MultiWidget,FileField):
    """
    Complete file upload with image cropper widget
    """
    
    def __init__(self,attrs=None):
        widgets = (AdminFileWidget(attrs=attrs),
                   #TextInput(attrs=attrs),
                   ImageCropCoordinatesInput(attrs=attrs),
                   )
        super(CroppedImageFileInput,self).__init__(widgets,attrs)
     
    def decompress(self,value):
        if isinstance(value,CroppedImageFile):
            return [value,value]
        return [None,None]
    
    def value_from_datadict(self, data, files, name):
        # Maybe have it return a different class if the file isn't uploaded
        
        values = super(CroppedImageFileInput,self).value_from_datadict(data,files,name)
        if isinstance(values[0],File):
            file = CroppedImageFile(values[0])
        else:
            file = CroppedImageFile(None)
        file.crop_coords = values[1]
        return file
        #return None
     
    def _has_changed(self,initial,data):
        if data.file:
            # file changed
            return True
        #changed = super(CroppedImageFileInput,self)._has_changed(initial,data)
        return initial.crop_coords != data.crop_coords
    
class HiddenCroppedImageFileInput(CroppedImageFileInput):
    """
    Splits the cropped image file input into two hidden inputs
    """
    def __init__(self,attrs=None):
        super(HiddenCroppedImageFileInput,self).__init__(attrs)
        
        self.widgets=(FileInput(attrs=attrs),
                   ImageCropCoordinatesInput(attrs=attrs),
                   ) 

        
        for widget in self.widgets:
            widget.input_type = 'hidden'
            widget.is_hidden = True
    
#    def render (self,name,value, attrs=None):
#        text= super(CroppedImageFileInput,self).render(name,value,attrs)
#        return text + "Hello World"
#    def render(self, name, value, attrs=None):
#        output=[]
#        
#        final_attrs = self.build_attrs(attrs)
#        id_ = final_attrs.get('id', None)
#        
#        #Rendering the File widget
#        fileParamName = "%s_%s" %(name,"file")
#        
#        if id_:
#            final_attrs = dict(final_attrs,id='%s_%s' % (id_,'file',))
#        output.append( self.fileInputWidget.render(fileParamName,value,final_attrs))
#        
#        return "".join(output)
    
#    def _get_media(self):
#        """Media for a multiwidget is the combination of all media of the subwidgets"""
#        media = Media()
#        media = media + self.fileInputWidget
#        media = media + self.imageCropWidget
#        return media
#    
#    media = property(_get_media)
        
        
        
            