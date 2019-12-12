from django.core.management.base import BaseCommand
from web.models import Resource


class Command(BaseCommand):
    help = "Exports emails"

    def handle(self, *args, **options):
        emails = []
        for resource in Resource.objects.filter(post_status='publish', year=settings.OEW_YEAR):
            emails.append(resource.email)

        for email in set(emails):
            print("{},".format(email))
