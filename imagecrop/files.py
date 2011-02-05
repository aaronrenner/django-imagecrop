'''
Created on Jan 22, 2011

@author: arenner
'''

from django.core.files.images import ImageFile
import json

class CropCoords(object):
    '''
    This class represents crop coordinates
    '''
    
    def __init__(self, x1=None, y1=None, x2=None, y2=None):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        
    def __eq__(self,other):
        return other and \
            self.x1 == other.x1 and \
            self.y1 == other.y1 and \
            self.x2 == other.x2 and \
            self.y2 == other.y2
            
    def __ne__(self,other):
        return not self.__eq__(other)
    
    def __hash__(self):
        # Required because we are defining a custom __eq__.
        return hash(self.__str__())
    
    def __str__(self):
        return {'x1':self.x1, 'y1':self.y1, 'x2':self.x2, 'y2':self.y2}.__str__()
        
class CropCoordEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, CropCoords):
            return {'__CropCoords__': True, 'x1':obj.x1, 'y1':obj.y1, 'x2':obj.x2, 'y2':obj.y2}
        return json.JSONEncoder.default(self, obj)

def decode_crop_coord(dct):
    if '__CropCoords__' in dct:
        return CropCoords(dct['x1'],dct['y1'],dct['x2'],dct['y2'])
    return dct
        

class CroppedImageFile(ImageFile):
    def __init__(self, file, name=None, crop_coords=None):
        self._crop_coords = crop_coords
        super(CroppedImageFile, self).__init__(file, name)
        
    def _get_crop_coords(self):
        return self._crop_coords
    
    def _set_crop_coords(self, value):
        if value and not isinstance(value, CropCoords):
            raise ValueError("Cannot set crop_coords to an object that is not of type CropCoords")
        self._crop_coords = value
    
    crop_coords = property(_get_crop_coords, _set_crop_coords, None, "Gets and sets a dictionary of crop coordinates (keys: x1,y1,x2,y2)")
