from django.core.management.base import BaseCommand, CommandError
from django.db.models import F, ExpressionWrapper, fields, DurationField
from django.db import models

from ya.common.models import Citizen


class Command(BaseCommand):
    def handle(self, *args, **options):
        import_id = 2

        t = Citizen.objects.annotate(diff=F('birth_date'), output_field=models.DateField())
        print(t)
        # citizens = Citizen.objects.filter(import_id=import_id)

        print(1)


