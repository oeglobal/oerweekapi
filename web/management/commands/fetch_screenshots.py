from django.core.management.base import BaseCommand
from web.models import Resource


class Command(BaseCommand):
    help = "Exports emails"

    def handle(self, *args, **options):
        for resource in Resource.objects.filter(screenshot_status__in=['', 'PENDING'], created__year=2017, post_status__in=['draft', 'publish']):
            print(resource.id)
            resource.get_screenshot()
