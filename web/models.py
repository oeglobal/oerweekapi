from django.db import models

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

    class Meta:
        abstract = True

class OpenPhoto(TimeStampedModel, ReviewModel):
    title = models.CharField(max_length=255)
    url = models.URLField(max_length=255)
    country = models.CharField(max_length=255)
    city = models.CharField(max_length=255)

    def __str__(self):
        return self.title
