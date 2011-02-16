from django.conf.urls.defaults import *

urlpatterns=patterns('',
    url(r'^crop_popup/$','imagecrop.views.imagecrop_popup')          
)
