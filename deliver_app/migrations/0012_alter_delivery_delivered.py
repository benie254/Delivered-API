# Generated by Django 4.2.2 on 2023-06-12 12:50

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deliver_app', '0011_alter_delivery_delivered'),
    ]

    operations = [
        migrations.AlterField(
            model_name='delivery',
            name='delivered',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2023, 6, 12, 15, 50, 39, 357757), null=True),
        ),
    ]