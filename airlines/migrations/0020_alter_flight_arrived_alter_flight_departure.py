# Generated by Django 4.2 on 2023-05-14 20:19

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('airlines', '0019_alter_flight_arrived_alter_flight_departure'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flight',
            name='arrived',
            field=models.DateTimeField(default=datetime.timezone),
        ),
        migrations.AlterField(
            model_name='flight',
            name='departure',
            field=models.DateTimeField(default=datetime.timezone),
        ),
    ]