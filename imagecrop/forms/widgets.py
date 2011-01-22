'''
Created on Jan 19, 2011

@author: arenner
'''
from django.forms.widgets import Widget, HiddenInput
from django.template import Template, Context
from django.utils.safestring import mark_safe 

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
    
    def __init__(self,image_url,attrs=None,aspect_ratio=0.0, crop_image_height=None, crop_image_width=None):
        '''
        Creates a new ImageCrop input
        
        attrs - HTML attributes
        aspect_ratio - width/height. 0 for N/A. 1.0 for square
        crop_image_height - The max height of the image cropping control
        crop_image_width - The max width of the image cropping control
        '''
        super(ImageCropCoordinatesInput,self).__init__(attrs)
        
        self.image_url=image_url
        self.aspect_ratio=aspect_ratio
        self.crop_image_height = crop_image_height
        self.crop_image_width = crop_image_width
        
        
        
        
    
    #def decompress(self,value):
    #    if value:
    #        return value
    #    return [None,None,None,None]
    
    def render(self, name, value, attrs=None):
        if value is None:
            value={}
        
        output = []
        
        final_attrs = self.build_attrs(attrs)
        id_ = final_attrs.get('id', None)
        
        
                      
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
               "imageurl": self.image_url,
               "coords": value,
               "boxWidth": self.crop_image_width,
               "boxHeight":self.crop_image_height,
               })
        output.append(t.render(c))
           
        for param in ImageCropCoordinatesInput.COORD_PARAMS:
            widget = HiddenInput()
            
            if id_:
                final_attrs = dict(final_attrs,id='%s_%s' % (id_, param))
            output.append(widget.render("%s_%s" % (name,param),value.get(param,None),final_attrs))
            
        return mark_safe(u''.join(output))
    
    def value_from_datadict(self, data, files, name):
        result = {}
        
        for param in ImageCropCoordinatesInput.COORD_PARAMS:
            result[param]= data.get(u"%s_%s" % (name,param,),None)
        return result
        
        

#class CroppedImageFileInput(MultiWidget):
#    """
#    Complete file upload with image cropper widget
#    """
    
#    def __init__(self):
#        pass