import random

from django.core.management.base import BaseCommand, CommandParser

from apps.tasks.models import Task, Requirements, TolType


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            'num_req',
            type=int
            )

    def handle(self, *args, **options):
        req_payloads = list()
        tasks = Task.objects.active().all().iterator()

        while len(req_payloads) < options["num_req"]:
            new_requirement = {}
            new_requirement["is_active"] = True
            new_requirement["due_months"] = random.randrange(1, 36)
            new_requirement["due_months_unit"] = random.choice(TolType.provide_choice_types("DUE_UNIT"))
            new_requirement["tol_pos_mos"] = random.randrange(0, 20)
            new_requirement["tol_neg_mos"] = random.randrange(0, 20)
            new_requirement["tol_mos_unit"] = random.choice(TolType.provide_choice_types("MOS_UNIT"))
            req_payloads.append(new_requirement)

        for task, req_payload in zip(tasks, req_payloads):
            new_requirement = Requirements.objects.create(task=task, **req_payload)
            new_requirement.save()
