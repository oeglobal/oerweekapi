from django.contrib import admin

from .models import OpenPhoto

class OpenPhotoAdmin(admin.ModelAdmin):
    pass

admin.site.register(OpenPhoto, OpenPhotoAdmin)
