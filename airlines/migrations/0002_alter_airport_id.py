# Generated by Django 4.2 on 2023-04-21 12:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('airlines', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='airport',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
