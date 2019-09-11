from django.db import models
from user_app.models import UserInfo, User_order, Adress
from integral_app.models import Pro_sku


# Create your models here.
#
# # 购物车CartInfo
# # id
# # user 用户（关联UserInfo）
# # pros 商品（关联Pro_sku）
# # ccount 数量（数量）
class CartInfo(models.Model):
    ccount = models.IntegerField(default=1, verbose_name='商品数量')
    pros = models.ForeignKey(Pro_sku, on_delete=models.CASCADE, verbose_name='商品')
    user = models.ForeignKey(UserInfo, on_delete=models.CASCADE, verbose_name='用户')
    cprice = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品总价')

    class Meta:
        # ordering = ['up_time']
        verbose_name = '购物车'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.user.username


# 订单商品表Order
# id  ：索引订单详情
# pro_id  : 商品ID （关联 Pro_sku）
# oprice  : 商品单价
# ocount  ： 商品数量
# oprices ： 商品总价
class Order(models.Model):
    order = models.ForeignKey(User_order, on_delete=models.CASCADE, verbose_name='订单信息表')
    count = models.IntegerField(default=1, verbose_name='商品数量')
    prices = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='小计')
    pro_id = models.ForeignKey(Pro_sku, on_delete=models.CASCADE, verbose_name='商品sku')
    comment = models.CharField(max_length=200, default='', verbose_name='留言评论')

    class Meta:
        verbose_name = '订单商品表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "%s 由用户 '%s'下单，%s" % (self.pro_id.name, self.order.user.username, self.order.pay_time)
