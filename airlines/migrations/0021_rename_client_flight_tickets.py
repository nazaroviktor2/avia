# Generated by Django 4.2 on 2023-05-14 20:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('airlines', '0020_alter_flight_arrived_alter_flight_departure'),
    ]

    operations = [
        migrations.RenameField(
            model_name='flight',
            old_name='client',
            new_name='tickets',
        ),
    ]