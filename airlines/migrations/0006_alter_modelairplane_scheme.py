# Generated by Django 4.2 on 2023-05-08 17:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('airlines', '0005_client_flight_alter_modelairplane_load_capacity_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='modelairplane',
            name='scheme',
            field=models.JSONField(),
        ),
    ]
