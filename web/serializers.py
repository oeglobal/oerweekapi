from pprint import pprint
import arrow

from django.template.defaultfilters import truncatewords_html
from rest_framework import serializers

from .models import Page, Resource, EmailTemplate


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
                  'event_facilitator', 'linkwebroom'
                  )
        read_only_fields = ('content_excerpt',)

    def get_content_excerpt(self, obj):
        return truncatewords_html(obj.content, 30)


class SubmissionResourceSerializer(serializers.HyperlinkedModelSerializer):
    institutionurl = serializers.CharField(source='institution_url', allow_blank=True)
    language = serializers.CharField(source='form_language')
    eventtype = serializers.CharField(source='event_type', allow_blank=True, allow_null=True, required=False)
    description = serializers.CharField(source='content')

    directions = serializers.CharField(source='event_directions', allow_blank=True, allow_null=True)
    image_url = serializers.CharField(source='get_image_url', read_only=True)
    post_status = serializers.CharField(read_only=True, required=False)

    license = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    slug = serializers.CharField(allow_null=True, required=False)
    linkwebroom = serializers.CharField(allow_blank=True)

    class Meta:
        model = Resource
        fields = ('id', 'firstname', 'lastname', 'institution', 'institutionurl', 'email',
                  'country', 'city', 'language',
                  'eventtype', 'event_time',
                  'title', 'description', 'event_time', 'directions', 'link', 'linkwebroom',
                  'opentags', 'license', 'post_status', 'image_url', 'slug', 'post_type'
                  )

    def validate_institutionurl(self, value):
        if value and not value.startswith('http'):
            value = 'http://' + value

        return value

    def validate_link(self, value):
        if value and not value.startswith('http'):
            value = 'http://' + value

        return value

    def validate_linkwebroom(self, value):
        if value and not value.startswith('http'):
            value = 'http://' + value

        return value

    def to_internal_value(self, data):
        if data.get('linkwebroom') is None:
            data['linkwebroom'] = ''

        return super().to_internal_value(data)

    def create(self, validated_data):
        data = validated_data
        data['post_status'] = 'draft'

        if data.get('post_type') == 'event' and data.get('event_type') == 'online':
            data['event_online'] = True
        else:
            data['event_type'] = ''

        if not data.get('license'):
            data['license'] = ''

        resource = Resource.objects.create(**data)
        resource.send_new_submission_email()

        return resource


class AdminSubmissionResourceSerializer(SubmissionResourceSerializer):
    post_status = serializers.CharField(read_only=False)


class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = ('id', 'name', 'subject', 'body')
