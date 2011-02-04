"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from imagecrop.files import CroppedImageFile
from testapp import models

class CroppedImageFieldTest(TestCase):
    
    def testSimpleCoordStorage(self):
        test_coords = [[40,20],[500,300]]
        
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

    def testChangeCoordsNoSave(self):
        test_coords = [[40,20],[500,300]]
        
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
        
    def testNoCoords(self):
        test_coords = [[40,20],[500,300]]
        
        file = CroppedImageFile(open('static/images/test.jpg'))
        # Save file
        img = models.TestImage(image=file,name="My Test")
        self.assertEqual(img.image.crop_coords, None)
        img.save()
        
           
        #Fetch model
        new_img = models.TestImage.objects.get(name="My Test")
        
        self.assertEqual(None, new_img.image.crop_coords)