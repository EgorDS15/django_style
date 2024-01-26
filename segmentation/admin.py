from django.contrib import admin
# Делаем импорт наших классов таблиц
from segmentation.models import ImagesForSegmentation


# Register your models here.(Регистрируем)
admin.site.register(ImagesForSegmentation)