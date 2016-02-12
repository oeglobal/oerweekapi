from django.db import models
from django.conf import settings
from taggit.managers import TaggableManager

from model_utils import Choices
from model_utils.models import TimeStampedModel

class ReviewModel(models.Model):
    REVIEW_CHOICES = Choices(
        ('new', 'New Entry'),
        ('feedback', 'Requested feedback'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    )
    status = models.CharField(choices=REVIEW_CHOICES, default='new', max_length=16)
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)

    class Meta:
        abstract = True

class OpenPhoto(TimeStampedModel, ReviewModel):
    POST_STATUS_TYPES = Choices(
        ('publish', 'Publish'),
        ('draft', 'Draft'),
        ('trash', 'Trash')
    )

    post_status = models.CharField(choices=POST_STATUS_TYPES, max_length=25, blank=True)
    post_id = models.IntegerField(null=True)
    title = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, blank=True)
    content = models.TextField(blank=True)

    lat = models.FloatField(null=True)
    lng = models.FloatField(null=True)
    address = models.CharField(blank=True, max_length=1024)

    url = models.URLField(max_length=255, blank=True)
    country = models.CharField(max_length=255)
    city = models.CharField(max_length=255)

    def __str__(self):
        return self.title

    def refresh(self):
        from .importer import import_openphoto
        import_openphoto(post_id=self.post_id)

class Page(TimeStampedModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    content = models.TextField(blank=True)

    def __str__(self):
        return self.title

class Category(TimeStampedModel):
    '''Wordpress Category Taxonomy'''
    wp_id = models.IntegerField()
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)

class Resource(TimeStampedModel, ReviewModel):
    RESOURCE_TYPES = Choices(
        ('resource', 'Resource'),
        ('project', 'Project'),
        ('event', 'Event')
    )

    POST_STATUS_TYPES = Choices(
        ('publish', 'Publish'),
        ('draft', 'Draft'),
        ('trash', 'Trash')
    )

    EVENT_TYPES = Choices(
        ('conference/forum/discussion', 'conference/forum/discussion'),
        ('webinar', 'webinar'),
        ('workshop', 'workshop'),
        ('local', 'local'),

    )

    post_type = models.CharField(choices=RESOURCE_TYPES, max_length=25)
    post_status = models.CharField(choices=POST_STATUS_TYPES, max_length=25)
    post_id = models.IntegerField()
    title = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, blank=True)
    content = models.TextField(blank=True)

    form_id = models.IntegerField(blank=True, null=True)
    contact = models.CharField(max_length=255, blank=True)
    institution = models.CharField(max_length=255, blank=True)
    form_language = models.CharField(max_length=255, blank=True)
    license = models.CharField(max_length=255, blank=True)
    link = models.CharField(max_length=255, blank=True)

    image_url = models.URLField(blank=True, null=True)

    city = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255, blank=True)

    event_time = models.DateTimeField(blank=True, null=True)
    event_type = models.CharField(max_length=255, blank=True, choices=EVENT_TYPES)
    event_source_datetime = models.CharField(max_length=255, blank=True)
    event_source_timezone = models.CharField(max_length=255, blank=True)

    lat = models.FloatField(null=True)
    lng = models.FloatField(null=True)
    address = models.CharField(blank=True, max_length=1024)

    categories = models.ForeignKey(Category, null=True)
    tags = TaggableManager()

    def refresh(self):
        from .importer import import_resource
        import_resource(post_type=self.post_type, post_id=self.post_id)
