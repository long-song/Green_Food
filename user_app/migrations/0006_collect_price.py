# Generated by Django 2.1.8 on 2019-07-31 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_app', '0005_collect'),
    ]

    operations = [
        migrations.AddField(
            model_name='collect',
            name='price',
            field=models.DecimalField(decimal_places=2, default=40.0, max_digits=10, verbose_name='单价'),
        ),
    ]
