from django.core.management.base import BaseCommand

from apps.tasks.models import Task


class Command(BaseCommand):

    def handle(self, *args, **options):
        tasks = Task.objects.all()
        tasks.delete()
