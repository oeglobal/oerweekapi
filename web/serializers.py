from django.template.defaultfilters import truncatewords_html
from rest_framework import serializers

from .models import OpenPhoto, Page, Resource

class OpenPhotoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OpenPhoto
        fields = ('id', 'title', 'url', 'country', 'city', 'status',
                'post_status', 'post_id', 'slug', 'content')
        read_only_fields = ('status', 'title')

    def save(self):
        super().save()

        if not self.instance.status:
            self.instance.status = 'new'
            self.instance.save()

        if not self.instance.title:
            self.instance.title = 'OpenPhoto #{}'.format(self.instance.id)
            self.instance.save()

        return self.instance

class AuthenticatedOpenPhotoSerializer(OpenPhotoSerializer):
    class Meta:
        model = OpenPhoto
        fields = ('id', 'title', 'url', 'country', 'city', 'status')
        read_only_fields = ('title',)

class PageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Page
        fields = ('id', 'title', 'slug', 'content')

class ResourceSerializer(serializers.HyperlinkedModelSerializer):
    content_excerpt = serializers.SerializerMethodField()

    class Meta:
        model = Resource
        fields = ('id', 'title', 'post_type', 'post_status', 'post_id',
                'title', 'slug', 'content', 'contact', 'institution',
                'form_language', 'license', 'link', 'categories',
                'content_excerpt', 'image_url', 'country', 'city',
                'event_time', 'event_type',
                'event_source_datetime', 'event_source_timezone'
                )
        read_only_fields = ('content_excerpt',)

    def get_content_excerpt(self, obj):
        return truncatewords_html(obj.content, 30)
