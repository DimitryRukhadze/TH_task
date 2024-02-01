import random
import string

from django.core.management.base import BaseCommand, CommandParser

from apps.tasks.models import Task


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            'num_tasks',
            type=int
            )

    def handle(self, *args, **options):
        task_names = set()

        while len(task_names) < options["num_tasks"]:
            t_name = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
            task_names.add(t_name)

        tasks_payload = dict.fromkeys([*task_names])

        for name in tasks_payload:
            description = "".join(random.choices(string.ascii_uppercase + string.ascii_lowercase, k=15))
            tasks_payload[name] = description

        tasks = [
            Task(code=key, description=value)
            for key, value in tasks_payload.items()
        ]

        Task.objects.bulk_create(tasks)
