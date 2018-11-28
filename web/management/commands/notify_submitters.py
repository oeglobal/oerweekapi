from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.template.loader import get_template

from web.models import Resource


class Command(BaseCommand):
    help = "Notifies submitters that they got accepted"

    def handle(self, *args, **options):
        plaintext = get_template('emails/accepted.txt')

        for resource in Resource.objects.filter(post_status='publish',
                                                created__year=2009,
                                                notified=False).exclude(email='')[:15]:
            if Resource.objects.filter(email=resource.email, notified=True).count():
                print('Skipping {} about #{}'.format(resource.email, resource.id))

                resource.notified = True
                resource.save()

                continue

            resource.notified = True
            resource.save()

            send_mail('Your Open Education Week submission has been approved', plaintext.render({}),
                      'info@openeducationweek.org', [resource.email], fail_silently=False)

            print('Emailed {} about #{}'.format(resource.email, resource.id))
