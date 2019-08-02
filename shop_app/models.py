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
    user = models.ForeignKey(UserInfo, on_delete=models.CASCADE)
    pros = models.ForeignKey(Pro_sku, on_delete=models.CASCADE)
    ccount = models.IntegerField('数量',default=1)
    cprice = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='小计')

    def __str__(self):
        return self.user


# 订单详情表Order
# id  ：索引订单详情
# pro_id  : 商品ID （关联 Pro_sku）
# oprice  : 商品单价
# ocount  ： 商品数量
# oprices ： 商品总价
class Order(models.Model):
    ccount = models.IntegerField()
    pros = models.ForeignKey(Pro_sku, models.DO_NOTHING)
    user = models.ForeignKey(UserInfo, models.DO_NOTHING)
    cprice = models.DecimalField(max_digits=10, decimal_places=2)

