# Generated by Django 4.2.2 on 2023-06-11 23:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deliver_app', '0002_monthlycumulative_delivery'),
    ]

    operations = [
        migrations.AddField(
            model_name='monthlycumulative',
            name='month',
            field=models.CharField(blank=True, default='', max_length=1000, null=True),
        ),
    ]
