from django.db import models
from user_app.models import UserInfo, User_order, Adress
from integral_app.models import Pro_sku


# Create your models here.

# 购物车CartInfo
# id
# user 用户（关联UserInfo）
# pros 商品（关联Pro_sku）
# ccount 数量（数量）
class CartInfo(models.Model):
    ccount = models.IntegerField()
    pros = models.ForeignKey(Pro_sku, models.DO_NOTHING)
    user = models.ForeignKey(UserInfo, models.DO_NOTHING)
    cprice = models.DecimalField(max_digits=10, decimal_places=2)


    def __str__(self):
        return self.user
    class Meta:
        # ordering = ['up_time']
        verbose_name = '购物车'
        verbose_name_plural = '购物车'


# 订单详情表Order
# id  ：索引订单详情
# pro_id  : 商品ID （关联 Pro_sku）
# oprice  : 商品单价
# ocount  ： 商品数量
# oprices ： 商品总价
class Order(models.Model):
    oprice = models.DecimalField(max_digits=5, decimal_places=2)
    ocount = models.IntegerField()
    oprices = models.DecimalField(max_digits=8, decimal_places=2)
    pro_id = models.ForeignKey(Pro_sku, models.DO_NOTHING)
    oadress = models.ForeignKey(Adress, models.DO_NOTHING, blank=True, null=True)
    class Meta:
        # ordering = ['up_time']
        verbose_name = '确认订单管理'
        verbose_name_plural = '确认订单管理'
