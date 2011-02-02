from django.db import models
from imagecrop.db.fields import CroppedImageField

# Create your models here.
class TestImage(models.Model):
    name=models.CharField(max_length=50)
    image = CroppedImageField(upload_to="test")