"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from imagecrop.files import CroppedImageFile, CropCoords
from testapp import models
import os

class CroppedImageFieldTest(TestCase):
    
    def testSimpleCoordStorage(self):
        test_coords = CropCoords(40,20,500,300)
        
        file = CroppedImageFile(open('static/images/test.jpg'))
        file.crop_coords=test_coords
        # Save file
        img = models.TestImage(image=file,name="My Test")
        img.save()
        
        
        
        #Fetch model
        new_img = models.TestImage.objects.get(name="My Test")
        
        self.assertNotEqual(new_img,None)
        self.assertEqual(img.image, new_img.image)
        self.assertEqual(test_coords, new_img.image.crop_coords)
        
        #Delete to cleanup
        new_img.delete()

    def testChangeCoordsNoSave(self):
        test_coords = CropCoords(40,20,500,300)
        
        file = CroppedImageFile(open('static/images/test.jpg'))
        file.crop_coords=test_coords
        # Save file
        img = models.TestImage(image=file,name="My Test")
        img.image.crop_coords = None
        self.assertEqual(img.image.crop_coords, None)
        img.save()
        
           
        #Fetch model
        new_img = models.TestImage.objects.get(name="My Test")
        
        self.assertEqual(img.image, new_img.image)
        self.assertEqual(None, new_img.image.crop_coords)
        
        #Try changing coords on fetched model and see if it takes
        new_coords = CropCoords(10,10,20,20)
        new_img.image.crop_coords=new_coords
        self.assertEqual(new_coords,new_img.image.crop_coords)
        
        #Delete to cleanup
        new_img.delete()
        
    def testNoCoords(self):
        '''
        Tests saving the model with no coords
        '''
        
        file = CroppedImageFile(open('static/images/test.jpg'))
        # Save file
        img = models.TestImage(image=file,name="My Test")
        self.assertEqual(img.image.crop_coords, None)
        img.save()
        
           
        #Fetch model
        new_img = models.TestImage.objects.get(name="My Test")
        
        self.assertEqual(None, new_img.image.crop_coords)
        
        #Delete to cleanup
        new_img.delete()
    
    def testDelete(self):
        '''
        Tests deleting the model and makes sure the appropriate cleanup occurs
        '''
        
        file = CroppedImageFile(open('static/images/test.jpg'))
        # Save file
        img = models.TestImage(image=file,name="My Test")
        self.assertEqual(img.image.crop_coords, None)
        img.save()
        
        meta_filename = img.image.get_meta_filename()
        
        img.delete()
        
        self.assertFalse( os.path.exists(meta_filename))
        