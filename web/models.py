from django.db import models
from django.conf import settings

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
    title = models.CharField(max_length=255, blank=True)
    url = models.URLField(max_length=255)
    country = models.CharField(max_length=255)
    city = models.CharField(max_length=255)

    def __str__(self):
        return self.title

class Page(TimeStampedModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    content = models.TextField(blank=True)

    def __str__(self):
        return self.title
