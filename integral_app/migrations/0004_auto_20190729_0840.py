# Generated by Django 2.1.8 on 2019-07-29 00:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('integral_app', '0003_auto_20190725_0855'),
    ]

    operations = [
        migrations.AddField(
            model_name='pro_sku',
            name='describe',
            field=models.CharField(max_length=600, null=True, verbose_name='产品介绍'),
        ),
        migrations.AddField(
            model_name='pro_sku',
            name='size',
            field=models.CharField(default='500g', max_length=10, verbose_name='产品规格'),
        ),
    ]
