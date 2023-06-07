# Generated by Django 4.2 on 2023-05-14 19:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.base
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('airlines', '0013_alter_client_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, validators=[django.db.models.base.Model.validate_unique]),
        ),
    ]