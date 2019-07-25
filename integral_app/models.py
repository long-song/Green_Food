from django.db import models
from user_app.models import UserInfo


# Create your models here.

# 商品分类表
class Pro_Type(models.Model):
    title = models.CharField('分类名称', max_length=30)
    desc = models.CharField('描述', max_length=200, default='商品描述')
    is_delete = models.BooleanField('删除', default=False)

    def __str__(self):
        return self.title


class Pro_sku(models.Model):
    '''
    商品SKU基本信息表
    '''
    image = models.ImageField(upload_to='static/images', default='images/product_AD_07.png', null=True, verbose_name='商品图片')
    name = models.CharField(max_length=50, verbose_name='商品名(规格)')
    title = models.CharField(max_length=100, verbose_name='标签')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='本店价')
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='市场价')
    stock = models.IntegerField(default=0, verbose_name='库存')
    sales = models.IntegerField(default=0, verbose_name='销量')
    type = models.ForeignKey(Pro_Type, on_delete=models.CASCADE)
    comments = models.IntegerField(default=0, verbose_name='评价数')
    is_putaway = models.BooleanField(default=True, verbose_name='是否上架销售')

    class Meta:
        db_table = 'Pro_sku'
        verbose_name = '商品SKU'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s: %s' % (self.id, self.name)


# 商品评论表
# dis_pro : 评论的目标商品
# dis_content ：评论内容
# dis_user : 评论用户
class Pro_discass(models.Model):
    dis_pro = models.ForeignKey(Pro_sku, on_delete=models.CASCADE)
    dis_content = models.CharField(max_length=200, verbose_name="评论内容")
    dis_user = models.ForeignKey(UserInfo, on_delete=models.CASCADE)


# 评论回复表
# reply_dis : 回复的目标评论
# reply_content : 回复内容
# reply_user ： 回复用户
class Reply_dis(models.Model):
    reply_dis = models.ForeignKey(Pro_discass, on_delete=models.CASCADE)
    reply_content = models.CharField(max_length=200, verbose_name="回复内容")
    reply_user = models.ForeignKey(UserInfo, on_delete=models.CASCADE)


class Group_buy(models.Model):
    '''
    商品团购表
    '''
    group_pro = models.ForeignKey(Pro_sku, on_delete=models.CASCADE)
    stime = models.DateTimeField(default='2019-7-20 15:30:30')
    ltime = models.DateTimeField(default='2019-7-30 15:30:30')

    class Meta:
        db_table = 'group_buy'
        verbose_name = '商品团购表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.id
