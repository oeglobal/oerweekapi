from django.core.management.base import BaseCommand
from web.models import Resource


class Command(BaseCommand):
    help = "Fetches screenshots"

    def handle(self, *args, **options):
        for resource in Resource.objects.filter(screenshot_status__in=['', 'PENDING'], year=2017, post_status__in=['draft', 'publish']):
            print(resource.id)
            resource.get_screenshot()
