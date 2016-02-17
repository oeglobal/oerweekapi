from django.contrib import admin

from .models import OpenPhoto, Page, Resource

class ResourceAdmin(admin.ModelAdmin):
    list_display = ('post_id', 'title', 'post_status', 'country', 'event_type')
    readonly_fields = ('created', 'modified',)
    search_fields = ('post_id', 'title')
    list_filter = ('country', 'post_type', 'event_type', 'notified')

class OpenPhotoAdmin(admin.ModelAdmin):
    list_display = ('post_id', 'title', 'post_status')
    search_fields = ('content', 'url')


class PageAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    change_form_template = 'web/admin/change_form.html'

admin.site.register(Resource, ResourceAdmin)
admin.site.register(OpenPhoto, OpenPhotoAdmin)
admin.site.register(Page, PageAdmin)
