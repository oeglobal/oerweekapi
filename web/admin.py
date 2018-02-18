from django.contrib import admin

from .models import OpenPhoto, Page, Resource, Category, EmailTemplate


class ResourceAdmin(admin.ModelAdmin):
    list_display = ('post_id', 'title', 'post_status', 'country', 'event_type', 'contact', 'institution')
    readonly_fields = ('created', 'modified',)
    search_fields = ('post_id', 'title', 'country', 'contact', 'firstname', 'lastname', 'email', 'institution', 'link')
    list_filter = ('post_status', 'post_type', 'event_type', 'notified')


class OpenPhotoAdmin(admin.ModelAdmin):
    list_display = ('post_id', 'title', 'post_status')
    search_fields = ('content', 'url')


class PageAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    change_form_template = 'web/admin/change_form.html'


class CategoryAdmin(admin.ModelAdmin):
    pass


class EmailTemplateAdmin(admin.ModelAdmin):
    pass


admin.site.register(Resource, ResourceAdmin)
admin.site.register(OpenPhoto, OpenPhotoAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(EmailTemplate, EmailTemplateAdmin)
