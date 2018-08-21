import hashlib
import requests
import uuid
from urllib.parse import urlencode
from base64 import urlsafe_b64encode

from django.db import models
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils.text import slugify
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth import get_user_model

from taggit.managers import TaggableManager

from model_utils import Choices
from model_utils.models import TimeStampedModel

from mail_templated import send_mail

User = get_user_model()


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


class Page(TimeStampedModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    content = models.TextField(blank=True)

    def __str__(self):
        return self.title


class Category(TimeStampedModel):
    """Wordpress Category Taxonomy"""
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
        # duplicated due to legacy choices
        ('conference/forum/discussion', 'Conference/forum/discussion'),
        ('conference/seminar', 'Conference/seminar'),
        ('workshop', 'Workshop'),
        ('forum/panel/discussion', 'Forum/panel/discussion'),
        ('other_local', 'other_local'),
        ('local', 'local'),

        ('webinar', 'Webinar'),  # online
        ('discussion', 'Online Discussion'),  # online
        ('other_online', 'Other - Online'),  # online
        ('online', 'Online Event')
    )

    post_type = models.CharField(choices=RESOURCE_TYPES, max_length=25)
    post_status = models.CharField(choices=POST_STATUS_TYPES, max_length=25)
    post_id = models.IntegerField(default=0)
    title = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, blank=True)
    content = models.TextField(blank=True)

    form_id = models.IntegerField(blank=True, null=True)
    contact = models.CharField(max_length=255, blank=True)

    firstname = models.CharField(max_length=255, blank=True)
    lastname = models.CharField(max_length=255, blank=True)

    email = models.CharField(max_length=255, blank=True)
    institution = models.CharField(max_length=255, blank=True)
    institution_url = models.CharField(max_length=255, blank=True)
    form_language = models.CharField(max_length=255, blank=True)
    license = models.CharField(max_length=255, blank=True, null=True)
    link = models.CharField(max_length=255, blank=True)
    linkwebroom = models.CharField(max_length=255, blank=True)

    image_url = models.URLField(blank=True, null=True, max_length=500)

    city = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255, blank=True)

    event_time = models.DateTimeField(blank=True, null=True)
    event_type = models.CharField(max_length=255, blank=True, choices=EVENT_TYPES)
    event_online = models.BooleanField(default=False)
    event_source_datetime = models.CharField(max_length=255, blank=True)
    event_source_timezone = models.CharField(max_length=255, blank=True)
    event_directions = models.CharField(max_length=255, blank=True, null=True)
    event_other_text = models.CharField(max_length=255, blank=True)
    event_facilitator = models.CharField(max_length=255, blank=True)

    archive_planned = models.BooleanField(default=False)
    archive_link = models.CharField(max_length=255, blank=True)

    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)
    address = models.CharField(blank=True, max_length=1024)

    categories = models.ManyToManyField(Category, blank=True)
    tags = TaggableManager(blank=True)
    opentags = ArrayField(models.CharField(max_length=255, blank=True, ), blank=True)

    notified = models.BooleanField(default=False)
    raw_post = models.TextField(blank=True)

    screenshot_status = models.CharField(blank=True, default='', max_length=64)
    image = models.ImageField(upload_to='images/', blank=True)

    year = models.IntegerField(blank=True, null=True, default=settings.OEW_YEAR)
    oeaward = models.BooleanField(default=False)

    def get_full_url(self):
        if self.post_type == 'event':
            return "http://www.openeducationweek.org/events/{}".format(self.slug)

        return "http://www.openeducationweek.org/resources/{}".format(self.slug)

    def get_image_url(self):
        if self.image_url:
            return self.image_url
        if self.image:
            return self.image.url

    def save(self, *args, **kwargs):
        if not self.slug:
            next = 0
            while (not self.slug) or (Resource.objects.filter(slug=self.slug).exists()):
                self.slug = slugify(self.title)

                if next:
                    self.slug += '-{0}'.format(next)
                next += 1

        if self.firstname or self.lastname:
            self.contact = '{} {}'.format(self.firstname, self.lastname)

        super().save(*args, **kwargs)

    def get_screenshot(self):
        def webshrinker_v2(access_key, secret_key, url, params):
            params['key'] = access_key
            request = "thumbnails/v2/{}?{}".format(urlsafe_b64encode(url.encode()).decode(), urlencode(params, True))
            signed_request = hashlib.md5("{}:{}".format(secret_key, request).encode('utf-8')).hexdigest()

            return "https://api.webshrinker.com/{}&hash={}".format(request, signed_request)

        if self.image:
            self.screenshot_status = 'DONE'
            return self.save()
        print(self.link)

        if self.link and self.screenshot_status in ['', 'PENDING']:
            api_url = webshrinker_v2(settings.WEBSHRINKER_KEY, settings.WEBSHRINKEY_SECRET, self.link,
                                     {'size': '3xlarge'})
            print(api_url)
            response = requests.get(api_url)

            status_code = response.status_code

            if status_code == 200:
                self.image.save('screenshot_{}.png'.format(self.pk), ContentFile(response.content))
                self.screenshot_status = 'DONE'
                self.save()
            elif status_code == 202:
                self.screenshot_status = 'PENDING'
                self.save()
            else:
                print('Status code {}'.format(response.status_code))
                raise NotImplementedError

    def send_new_submission_email(self):
        send_mail('emails/submission_received.tpl', {},
                  'info@openeducationweek.org', [self.email]
                  )

    def send_new_account_email(self):
        email = self.email.lower()
        if not User.objects.filter(email=email).exists():
            user = User.objects.create(
                username=email,
                email=email,
                first_name=self.firstname,
                last_name=self.lastname,
                is_active=True
            )
            key = uuid.uuid4().hex
            user.set_password(key)
            user.save()

            send_mail('emails/account_created.tpl', {'user': user, 'key': key},
                      'info@openeducationweek.org', [self.email]
                      )


class EmailTemplate(models.Model):
    name = models.CharField(max_length=128)
    subject = models.CharField(max_length=255)
    body = models.TextField(help_text='You can use the following variables in body and title: ' +
                                      '{{title}}, {{name}}, {{link}}. HTML is not allowed.')

    def __str__(self):
        return self.name
