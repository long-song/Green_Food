# Generated by Django 2.1.8 on 2019-08-28 01:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('province_id', models.BigIntegerField()),
                ('city_id', models.BigIntegerField(unique=True)),
                ('city_name', models.CharField(max_length=64)),
            ],
            options={
                'verbose_name': '市级管理',
                'verbose_name_plural': '市级管理',
                'db_table': 'spzx_business_position_city',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='County',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city_id', models.BigIntegerField()),
                ('county_id', models.BigIntegerField(unique=True)),
                ('county_name', models.CharField(max_length=64)),
            ],
            options={
                'verbose_name': '县级管理',
                'verbose_name_plural': '县级管理',
                'db_table': 'spzx_business_position_county',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Province',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('province_id', models.BigIntegerField(unique=True)),
                ('province_name', models.CharField(max_length=32)),
            ],
            options={
                'verbose_name': '省级管理',
                'verbose_name_plural': '省级管理',
                'db_table': 'spzx_business_position_province',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Adress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('aname', models.CharField(max_length=50, verbose_name='收货人')),
                ('ads', models.CharField(max_length=300, verbose_name='地址')),
                ('aphone', models.CharField(max_length=20, verbose_name='电话')),
                ('area', models.CharField(max_length=50, null=True, verbose_name='地区')),
                ('postcode', models.CharField(max_length=20, null=True, verbose_name='邮编')),
                ('is_default', models.BooleanField(default=False, verbose_name='是否默认')),
            ],
            options={
                'verbose_name': '地址管理',
                'verbose_name_plural': '地址管理',
            },
        ),
        migrations.CreateModel(
            name='Collect',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pro_id', models.IntegerField(null=True, unique=True, verbose_name='商品id')),
                ('image', models.ImageField(null=True, upload_to='', verbose_name='商品图片')),
                ('name', models.CharField(max_length=50, verbose_name='商品名(规格)')),
                ('size', models.CharField(default='500g', max_length=10, verbose_name='产品规格')),
                ('title', models.CharField(max_length=100, verbose_name='标签')),
                ('price', models.DecimalField(decimal_places=2, default=40.0, max_digits=10, verbose_name='单价')),
            ],
            options={
                'verbose_name': '收藏管理',
                'verbose_name_plural': '收藏管理',
            },
        ),
        migrations.CreateModel(
            name='User_order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('orderNo', models.CharField(max_length=50, verbose_name='订单号')),
                ('orderdetail', models.TextField(verbose_name='订单详情')),
                ('adsname', models.CharField(max_length=30, verbose_name='收件人姓名')),
                ('adsphone', models.CharField(max_length=20, verbose_name='收件人电话')),
                ('ads', models.CharField(max_length=300, verbose_name='地址')),
                ('time', models.DateTimeField(auto_now=True, verbose_name='下单时间')),
                ('acot', models.IntegerField(default=1, verbose_name='总数')),
                ('acount', models.DecimalField(decimal_places=2, max_digits=8, verbose_name='订单总价')),
                ('orderstatus', models.IntegerField(choices=[(1, '未支付'), (2, '已支付'), (3, '订单取消')], default=1, verbose_name='订单状态')),
            ],
            options={
                'verbose_name': '订单管理',
                'verbose_name_plural': '订单管理',
            },
        ),
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=15, unique=True, verbose_name='用户名')),
                ('password', models.CharField(max_length=256, verbose_name='密码')),
                ('phone', models.CharField(max_length=11, unique=True, verbose_name='手机号')),
                ('head_img', models.ImageField(default='images/QQ图片20190822180730.jpg', upload_to='static/images', verbose_name='头像')),
                ('t_name', models.CharField(max_length=10, null=True, verbose_name='真实姓名')),
                ('gender', models.IntegerField(choices=[(1, '男'), (2, '女')], default=1, verbose_name='性别')),
                ('email', models.EmailField(max_length=254, null=True, unique=True, verbose_name='邮箱')),
                ('birthday', models.DateField(null=True, verbose_name='生日')),
                ('up_time', models.DateTimeField(auto_now_add=True, null=True, verbose_name='注册时间')),
                ('allow_order', models.IntegerField(default=0, verbose_name='订单管理权限')),
                ('allow_data', models.IntegerField(default=0, verbose_name='数据管理权限')),
                ('superuser', models.IntegerField(default=0, verbose_name='超级管理员')),
            ],
            options={
                'verbose_name': '用户',
                'verbose_name_plural': '用户',
            },
        ),
        migrations.AddField(
            model_name='user_order',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_app.UserInfo'),
        ),
        migrations.AddField(
            model_name='collect',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='user_app.UserInfo'),
        ),
        migrations.AddField(
            model_name='adress',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_app.UserInfo'),
        ),
    ]
