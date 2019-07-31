from django.db import models


# from integral_app.models import Pro_sku
# Create your models here.

# 用户表 UserInfo
# username ： 用户名
# password ： 密码
# phone ：手机号
# head_img ：用户头像
# t_name ： 真实姓名
# gender ： 性别
# email ： 邮箱
# up_time ： 注册时间
# allow_order ： 订单管理权限  1可以管理订单，0无此权限
# allow_data ： 数据管理权限  1可以对数据进行增改查，0无此权限
# superuser : 超级管理员  1可以删除数据，可以对有管理员权限的用户进行管理，0无此权限

class UserInfo(models.Model):
    sex = (
        (1, '男',),
        (2, '女',),
    )
    username = models.CharField(max_length=15, unique=True, verbose_name='用户名')
    password = models.CharField(max_length=256, verbose_name='密码')
    phone = models.CharField(unique=True, max_length=11, verbose_name='手机号')
    head_img = models.ImageField(upload_to='static/images', default='images/product_img_17.png', verbose_name='头像')
    t_name = models.CharField(max_length=10, null=True, verbose_name='真实姓名')
    gender = models.IntegerField(choices=sex, default=1, verbose_name='性别')
    email = models.EmailField(null=True, unique=True, verbose_name='邮箱')
    birthday = models.DateField(verbose_name='生日', null=True)
    up_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name='注册时间')
    allow_order = models.IntegerField(verbose_name="订单管理权限", default=0)
    allow_data = models.IntegerField(verbose_name="数据管理权限", default=0)
    superuser = models.IntegerField(verbose_name="超级管理员", default=0)

    def __str__(self):
        return self.username

    # class Meta:
    #     ordering = ['up_time']
    #     verbose_name = '用户'
    #     verbose_name_plural = '用户'


# 地址表 Adress
# aname : 收货人
# ads ： 地址
# aphone : 收货电话
# user ： 用户 (关联 UserInfo)

class Adress(models.Model):
    aname = models.CharField(verbose_name='收货人', max_length=50, null=False)
    ads = models.CharField(verbose_name='地址', max_length=300, null=False)
    aphone = models.CharField(verbose_name='电话', max_length=20, null=False)
    user = models.ForeignKey(UserInfo, on_delete=models.CASCADE)
    area = models.CharField(verbose_name='地区', max_length=50, null=True)
    postcode = models.CharField(verbose_name='邮编', max_length=20, null=True)

    def __str__(self):
        return self.aname


# 订单信息表 User_order
# orderNo 订单号
# orderdetail(商品，数量，单价，描述)
# adsname 收件人姓名
# adsphone 收件电话
# ads　地址
# user　用户（关联）
# time 时间
# acot 订单总数
# acount 订单总价
# orderstatus 状态
class User_order(models.Model):
    ORDERSTATUS = (
        (1, '未支付',),
        (2, '已支付',),
        (3, '订单取消',),
    )
    orderNo = models.CharField(verbose_name='订单号', max_length=50)
    orderdetail = models.TextField(verbose_name='订单详情')
    adsname = models.CharField(verbose_name='收件人姓名', max_length=30, null=False)
    adsphone = models.CharField(verbose_name='收件人电话', max_length=20, null=False)
    ads = models.CharField(verbose_name='地址', max_length=300)
    time = models.DateTimeField(auto_now=True, verbose_name='下单时间')
    acot = models.IntegerField(verbose_name='总数', default=1)
    acount = models.DecimalField(verbose_name='订单总价', max_digits=8, decimal_places=2)
    orderstatus = models.IntegerField(verbose_name='订单状态', choices=ORDERSTATUS, default=1)
    user = models.ForeignKey(UserInfo, on_delete=models.CASCADE)

    def __str__(self):
        return self.orderNo

# # 收藏表
# class Collect(models.Model):
#     user = models.ForeignKey(UserInfo,on_delete=models.CASCADE)
#     product = models.ForeignKey(Pro_sku,on_delete=models.CASCADE)
