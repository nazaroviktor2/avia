# Generated by Django 4.2 on 2023-04-21 12:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('airlines', '0002_alter_airport_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='airport',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]