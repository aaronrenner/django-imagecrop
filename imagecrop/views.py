from django.template.context import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

def imagecrop_popup(request):
    '''
    Renders the imagecrop popup
    '''
    
    return render_to_response('imagecrop/crop_popup.html',{ 
            'ADMIN_MEDIA_PREFIX':settings.ADMIN_MEDIA_PREFIX 
        },
        context_instance=RequestContext(request) #This makes the TEMPLATE_CONTEXT_PROCESSORS setting work
    )