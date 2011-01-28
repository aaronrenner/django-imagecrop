'''
Created on Jan 22, 2011

@author: arenner
'''

from django.core.files.images import ImageFile

class CroppedImageFile(ImageFile):
    def __init__(self, file, name=None, crop_coords=None):
        self._crop_coords = crop_coords
        super(CroppedImageFile, self).__init__(file, name)
        
    def _get_crop_coords(self):
        return self._crop_coords
    
    def _set_crop_coords(self, value):
        self._crop_coords = value
    
    crop_coords = property(_get_crop_coords, _set_crop_coords, None, "Gets and sets a dictionary of crop coordinates (keys: x1,y1,x2,y2)")
