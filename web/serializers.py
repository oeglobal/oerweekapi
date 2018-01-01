from django.template.defaultfilters import truncatewords_html
from rest_framework import serializers
import arrow

from .models import OpenPhoto, Page, Resource


class OpenPhotoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OpenPhoto
        fields = ('id', 'title', 'url', 'country', 'city', 'status',
                  'post_status', 'post_id', 'slug', 'content',
                  'lat', 'lng', 'address')
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
    image_url = serializers.CharField(source='get_image_url')

    class Meta:
        model = Resource
        fields = ('id', 'title', 'post_type', 'post_status', 'post_id',
                  'title', 'slug', 'content', 'contact', 'institution',
                  'form_language', 'license', 'link', 'categories',
                  'content_excerpt', 'image_url', 'country', 'city',
                  'event_time', 'event_type',
                  'event_source_datetime', 'event_source_timezone',
                  )
        read_only_fields = ('content_excerpt',)

    def get_content_excerpt(self, obj):
        return truncatewords_html(obj.content, 30)


class SubmissionResourceSerializer(serializers.HyperlinkedModelSerializer):
    institutionurl = serializers.CharField(source='institution_url', allow_blank=True)
    language = serializers.CharField(source='form_language')
    contributiontype = serializers.SerializerMethodField()
    eventtype = serializers.CharField(source='event_type', allow_blank=True)
    # eventother = serializers.CharField(source='event_other_text', allow_blank=True)
    description = serializers.CharField(source='content')
    datetime = serializers.SerializerMethodField()

    directions = serializers.CharField(source='event_directions', allow_blank=True, allow_null=True)
    # archive = serializers.BooleanField(source='archive_planned')

    # is_primary = serializers.SerializerMethodField()
    # is_higher = serializers.SerializerMethodField()
    # is_community = serializers.SerializerMethodField()

    image_url = serializers.CharField(source='get_image_url', allow_blank=True, allow_null=True)

    class Meta:
        model = Resource
        fields = ('id', 'firstname', 'lastname', 'institution', 'institutionurl', 'email',
                  'country', 'city', 'language', 'contributiontype', 'eventtype',
                  'title', 'description', 'datetime', 'directions', 'link', 'linkwebroom',
                  'opentags', 'license', 'post_status', 'image_url'
                  )

    def get_contributiontype(self, obj):
        if obj.post_type == 'event' and obj.event_online:
            return 'event_online'

        if obj.post_type == 'event' and not obj.event_online:
            return 'event_local'

        return obj.post_type

    def get_datetime(self, obj):
        if obj.event_time:
            return arrow.get(obj.event_time).isoformat()
