from django.db import models


# Create your models here.
class ImagesForSegmentation(models.Model):
    name = models.CharField(max_length=128)
    image = models.ImageField(null=True, blank=True, upload_to='client_image')
