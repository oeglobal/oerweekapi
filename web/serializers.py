from pprint import pprint  # noqa: F401

from django.template.defaultfilters import truncatewords_html
from django.core.files.images import get_image_dimensions
from rest_framework import serializers

from .models import Page, Resource, ResourceImage, EmailTemplate


class PageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Page
        fields = ('id', 'title', 'slug', 'content')


class ResourceSerializer(serializers.HyperlinkedModelSerializer):
    content_excerpt = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Resource
        fields = ('id', 'title', 'post_type', 'post_status', 'post_id',
                  'title', 'slug', 'content', 'contact', 'institution',
                  'form_language', 'license', 'link', 'categories',
                  'content_excerpt', 'image_url', 'country', 'city',
                  'event_time', 'event_type', 'opentags',
                  'event_source_datetime', 'event_source_timezone',
                  'event_facilitator', 'linkwebroom', 'twitter'
                  )
        read_only_fields = ('content_excerpt',)

    def get_content_excerpt(self, obj):
        return truncatewords_html(obj.content, 30)

    def get_image_url(self, obj):
        return obj.get_image_url(self.context['request'])


class SubmissionResourceSerializer(serializers.HyperlinkedModelSerializer):
    institutionurl = serializers.CharField(source='institution_url', allow_blank=True)
    language = serializers.CharField(source='form_language')
    event_type = serializers.CharField(allow_null=True, required=False)
    description = serializers.CharField(source='content')

    directions = serializers.CharField(source='event_directions', allow_blank=True, allow_null=True)
    image_url = serializers.SerializerMethodField(read_only=True)
    post_status = serializers.CharField(read_only=True, required=False)
    post_status_friendly = serializers.SerializerMethodField(read_only=True, required=False)

    license = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    slug = serializers.CharField(allow_null=True, required=False)
    linkwebroom = serializers.CharField(allow_blank=True)
    image = serializers.CharField(allow_blank=True, required=False, source='image_id')

    class Meta:
        model = Resource
        fields = ('id', 'firstname', 'lastname', 'institution', 'institutionurl', 'email',
                  'country', 'city', 'language',
                  'event_type', 'event_time', 'event_facilitator',
                  'title', 'description', 'event_time', 'directions', 'link', 'linkwebroom',
                  'opentags', 'license', 'image_url', 'slug', 'post_type',
                  'post_status', 'post_status_friendly', 'image', 'twitter'
                  )

    def get_post_status_friendly(self, obj):
        if obj.post_status == 'draft':
            return 'Waiting for review'
        elif obj.post_status == 'publish':
            return 'Published'
        elif obj.post_status == 'trash':
            return 'Rejected'

        return obj.post_status

    def get_image_url(self, obj):
        return obj.get_image_url(self.context['request'])

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

        if not data.get('license'):
            data['license'] = ''

        if data.get('image_id'):
            data['image'] = ResourceImage.objects.get(pk=data.get('image_id'))

        resource = Resource.objects.create(**data)
        resource.send_new_submission_email()
        resource.send_new_account_email()

        return resource


class AdminSubmissionResourceSerializer(SubmissionResourceSerializer):
    post_status = serializers.CharField(read_only=False)


class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = ('id', 'name', 'subject', 'body')


class ResourceImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceImage
        fields = ('id', 'image')

    def validate_image(self, value):
        if value.content_type not in ['image/png', 'image/jpeg', 'image/gif']:
            raise serializers.ValidationError('Image has to be in JPG or PNG format')

        width, height = get_image_dimensions(value)

        if width < 800 or height < 600:
            raise serializers.ValidationError('Image is too small. It has to be at least 800x600px')

        return value
