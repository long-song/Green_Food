from django.db import models


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
        (1, '男'),
        (2, '女'),
    )
    username = models.CharField(max_length=15, unique=True, verbose_name='用户名')
    password = models.CharField(max_length=256, verbose_name='密码')
    phone = models.CharField(unique=True, max_length=11, verbose_name='手机号')
    head_img = models.ImageField(upload_to='static/images', default='images/product_img_17.png', verbose_name='头像')
    t_name = models.CharField(max_length=10, null=True, verbose_name='真实姓名')
    gender = models.IntegerField(choices=sex, default=1, verbose_name='性别')
    email = models.EmailField(null=True, verbose_name='邮箱')
    birthday = models.DateField(verbose_name='生日', null=True)
    up_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name='注册时间')
    is_active = models.IntegerField(verbose_name='是否激活', default=0)
    allow_order = models.IntegerField(verbose_name="订单管理权限", default=0)
    allow_data = models.IntegerField(verbose_name="数据管理权限", default=0)
    superuser = models.IntegerField(verbose_name="超级管理员", default=0)

    class Meta:
        verbose_name = '用户管理'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


class Province(models.Model):
    province_id = models.BigIntegerField(unique=True)
    province_name = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = 'spzx_business_position_province'
        verbose_name = '省级管理'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.province_name


class City(models.Model):
    province_id = models.BigIntegerField()
    city_id = models.BigIntegerField(unique=True)
    city_name = models.CharField(max_length=64)

    class Meta:
        managed = False
        db_table = 'spzx_business_position_city'
        verbose_name = '市级管理'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.city_name


class County(models.Model):
    city_id = models.BigIntegerField()
    county_id = models.BigIntegerField(unique=True)
    county_name = models.CharField(max_length=64)

    class Meta:
        managed = False
        db_table = 'spzx_business_position_county'
        verbose_name = '县级管理'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.county_name


# 地址表 Adress
# aname : 收货人
# ads ： 地址
# aphone : 收货电话
# user ： 用户 (关联 UserInfo)

class Adress(models.Model):
    aname = models.CharField(verbose_name='收货人', max_length=50, null=False)
    ads = models.CharField(verbose_name='地址', max_length=300, null=False)
    province_name = models.ForeignKey('Province', on_delete=models.CASCADE, default=1)
    city_name = models.ForeignKey('City', on_delete=models.CASCADE, default=1)
    county_name = models.ForeignKey('County', on_delete=models.CASCADE, default=1)
    aphone = models.CharField(verbose_name='电话', max_length=20, null=False)
    user = models.ForeignKey(UserInfo, on_delete=models.CASCADE, verbose_name='用户')
    area = models.CharField(verbose_name='地区', max_length=50, null=True)
    postcode = models.CharField(verbose_name='邮编', max_length=20, null=True)
    is_default = models.BooleanField(default=False, verbose_name='是否默认')

    class Meta:
        verbose_name = '地址管理'
        verbose_name_plural = verbose_name

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
    PAY_METHODS = {
        '1': '货到付款',
        '2': '微信支付',
        '3': '支付宝',
        '4': '银联支付'
    }
    PAY_METHODS_ENUM = {
        'CASH': 1,  # 现金
        'ALIPAY': 2,  # 阿里支付
    }
    ORDER_STATUS__ENUM = {
        'UNPAID': 1,  # 待支付
        'UNSEND': 2,  # 代发货
        'UNRECEIVED': 3,  # 待收货
        'UNCOMMIT': 4,  # 待评价
        'FINISHED': 5,  # 已完成
    }
    ORDER_STATUS = {
        1: '待支付',  # 待支付
        2: '代发货',  # 代发货
        3: '待收货',  # 待收货
        4: '待评价',  # 待评价
        5: '已完成',  # 已完成
    }
    PAY_METHODS_CHOICES = (
        (1, '货到付款'),
        (2, '微信支付'),
        (3, '支付宝'),
        (4, '银联支付')
    )
    ORDER_STATUS_CHOICES = (
        (1, '待支付'),
        (2, '待发货'),
        (3, '待收货'),
        (4, '待评价'),
        (5, '已完成'),
    )
    order_id = models.CharField(verbose_name='订单id', max_length=128, primary_key=True)
    pay_No = models.CharField(verbose_name='支付编号', max_length=128, default='')
    user = models.ForeignKey(UserInfo, on_delete=models.CASCADE, verbose_name='用户')
    adress = models.ForeignKey(Adress, on_delete=models.CASCADE, blank=True, null=True, verbose_name='收货地址')
    total_count = models.IntegerField(verbose_name='总数目', default=1)
    total_price = models.DecimalField(verbose_name='订单总价', max_digits=8, decimal_places=2)
    transit_price = models.DecimalField(verbose_name='运费', max_digits=8, decimal_places=2, default=10.00)
    order_status = models.IntegerField(verbose_name='订单状态', choices=ORDER_STATUS_CHOICES, default=1)
    pay_method = models.IntegerField(verbose_name='支付方式', choices=PAY_METHODS_CHOICES, default=3)
    pay_time = models.DateTimeField(auto_now=True, verbose_name='下单时间')

    class Meta:
        verbose_name = '订单管理'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s由%s下单，%s' % (self.pay_time, self.user.username, self.ORDER_STATUS[self.order_status])
