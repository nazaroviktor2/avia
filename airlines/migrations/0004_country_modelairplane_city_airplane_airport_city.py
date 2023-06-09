# Generated by Django 4.2 on 2023-04-22 16:31

import airlines.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('airlines', '0003_alter_airport_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='ModelAirplane',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('seats', models.IntegerField()),
                ('load_capacity', models.DecimalField(decimal_places=2, max_digits=5)),
                ('scheme', models.FileField(upload_to="")),
            ],
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='airlines.country')),
            ],
        ),
        migrations.CreateModel(
            name='Airplane',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(max_length=100)),
                ('model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='airlines.modelairplane')),
            ],
        ),
        migrations.AddField(
            model_name='airport',
            name='city',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='airlines.city'),
        ),
    ]
