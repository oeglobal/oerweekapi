from django.core.management.base import BaseCommand
from web.models import Resource

class Command(BaseCommand):
    help = "Exports emails"

    def handle(self, *args, **options):
        emails = []
        for resource in Resource.objects.filter(post_status='publish', created__year=2016):
            emails.append(resource.email)

        for email in set(emails):
            print(email)
