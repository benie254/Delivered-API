# Generated by Django 4.2.2 on 2023-06-11 20:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('deliver_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='monthlycumulative',
            name='delivery',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='deliver_app.delivery'),
        ),
    ]
