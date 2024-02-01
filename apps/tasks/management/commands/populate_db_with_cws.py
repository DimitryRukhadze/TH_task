import random

from django.utils import timezone
from datetime import datetime
from django.core.management.base import BaseCommand, CommandParser

from apps.tasks.models import Task, CW


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            'num_cws',
            type=int
            )

    def handle(self, *args, **options):
        cws_perf_dates = set()
        year = timezone.now().year
        tasks = Task.objects.all()

        while len(cws_perf_dates) < options["num_cws"]:
            datestring = f"{random.randrange(1991, year)}-{random.randrange(1, 12)}-{random.randrange(1, 28)}"
            date = datetime.strptime(datestring, "%Y-%m-%d")
            cws_perf_dates.add(date)

        date_iter = iter(cws_perf_dates)
        tasks_iter = iter(tasks)

        for task, cw_1_date, cw_2_date in zip(tasks_iter, date_iter, date_iter):
            cw1 = CW.objects.create(task=task, perform_date=cw_1_date)
            cw2 = CW.objects.create(task=task, perform_date=cw_2_date)
            print("added cw1")
            print("added cw2")

            if cw1:
                cw1.save()
            if cw2:
                cw2.save()
