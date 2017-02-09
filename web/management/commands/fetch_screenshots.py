from django.core.management.base import BaseCommand
from web.models import Resource


class Command(BaseCommand):
    help = "Exports emails"

    def handle(self, *args, **options):
        for resource in Resource.objects.filter(screenshot_status='', created__year=2017, status__in=['draft', 'publish']):
            resource.get_screenshot()
