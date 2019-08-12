from django.db import models
from django.contrib.postgres.fields import ArrayField


class Citizen(models.Model):
    GENDERS = ['male', 'female']

    import_id = models.BigIntegerField(null=False)
    citizen_id = models.BigIntegerField(null=False)
    town = models.CharField(max_length=255, null=False)
    street = models.CharField(max_length=255, null=False)
    building = models.CharField(max_length=255, null=False)
    apartment = models.IntegerField(null=False)
    name = models.CharField(max_length=255, null=False)
    birth_date = models.DateField(null=False)
    gender = models.CharField(max_length=6, null=False)
    relatives = ArrayField(models.BigIntegerField(null=False), default=list)

    class Meta:
        unique_together = (
            ('import_id', 'citizen_id'),
        )
