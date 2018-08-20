from django.core.management.base import BaseCommand
from web.models import Resource


class Command(BaseCommand):
    help = "Backfills year of OEW"

    def handle(self, *args, **options):
        for resource in Resource.objects.all():
            if resource.created.year == 2015 and resource.created.month < 6:
                resource.year = 2015
            elif resource.created.year == 2016 and resource.created.month < 6:
                resource.year = 2016
            else:
                resource.year = 2017

            resource.save()
