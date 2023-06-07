# Generated by Django 4.2 on 2023-06-06 20:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('airlines', '0030_ticketbooking_pay_before_alter_ticketbooking_ticket'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticketbooking',
            name='status',
            field=models.CharField(choices=[('Waiting', 'Waiting'), ('Confirmed', 'Confirmed'), ('Cancelled', 'Cancelled')], default='Waiting', max_length=9),
        ),
    ]