# Generated by Django 2.2.3 on 2019-08-12 07:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0004_change_type_of_birthday_field'),
    ]

    operations = [
        migrations.CreateModel(
            name='Import',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
            ],
        ),
    ]