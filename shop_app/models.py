from django.db import models
from user_app.models import UserInfo,User_order,Adress
from integral_app.models import Pro_sku
# Create your models here.

# 购物车CartInfo
# id
# user 用户（关联UserInfo）
# pros 商品（关联Pro_sku）
# ccount 数量（数量）
class CartInfo(models.Model):
    user = models.ForeignKey(UserInfo, db_column='user_id',on_delete=models.CASCADE)
    pros = models.ForeignKey(Pro_sku, db_column='good_id',on_delete=models.CASCADE)
    ccount = models.IntegerField('数量', db_column='cart_count')

    def __str__(self):
        return self.user


# 订单详情表Order
# id  ：索引订单详情
# orderNo :订单号（索引为某订单的详情）
# pro_id  : 商品ID （关联 Pro_sku）
# oprice  : 商品单价
# ocount  ： 商品数量
# oprices ： 商品总价
class Order(models.Model):
    orderNo = models.ForeignKey(User_order, on_delete=models.CASCADE)
    pro_id = models.ForeignKey(Pro_sku, on_delete=models.CASCADE)
    oprice = models.DecimalField('单价', max_digits=5, decimal_places=2)
    ocount = models.IntegerField('数量')
    oprices = models.DecimalField('总价', max_digits=8, decimal_places=2)

    def __str__(self):
        return self.orderNo

