# Generated by Django 2.1.8 on 2019-09-12 09:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('integral_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pro_discass',
            name='dis_like',
            field=models.IntegerField(default=0, verbose_name='获赞数'),
        ),
        migrations.AddField(
            model_name='pro_discass',
            name='dis_time',
            field=models.DateField(auto_now_add=True, null=True, verbose_name='评论日期'),
        ),
        migrations.AddField(
            model_name='reply_dis',
            name='reply_like',
            field=models.IntegerField(default=0, verbose_name='获赞数'),
        ),
        migrations.AddField(
            model_name='reply_dis',
            name='reply_time',
            field=models.DateField(auto_now_add=True, null=True, verbose_name='回复日期'),
        ),
    ]
