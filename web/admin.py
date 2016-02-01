from django.contrib import admin

from .models import OpenPhoto, Page, Resource

class ResourceAdmin(admin.ModelAdmin):
    pass

class OpenPhotoAdmin(admin.ModelAdmin):
    pass

class PageAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    change_form_template = 'web/admin/change_form.html'

admin.site.register(Resource, ResourceAdmin)
admin.site.register(OpenPhoto, OpenPhotoAdmin)
admin.site.register(Page, PageAdmin)
