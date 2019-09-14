from django.db import models
from user_app.models import UserInfo


# Create your models here.

# 商品分类表
class Pro_Type(models.Model):
    title = models.CharField('分类名称', max_length=30)
    desc = models.CharField('描述', max_length=200, default='商品描述')
    is_delete = models.BooleanField('删除', default=False)

    class Meta:
        verbose_name = '商品分类'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class Pro_sku(models.Model):
    '''
    商品SKU基本信息表
    '''
    image = models.ImageField(upload_to='static/images', default='images/product_AD_07.png', null=True,
                              verbose_name='商品图片')
    name = models.CharField(max_length=50, verbose_name='商品名(规格)', null=True)
    describe = models.CharField(max_length=600, verbose_name='产品介绍', null=True)
    size = models.CharField(max_length=10, default='500g', verbose_name='产品规格')
    title = models.CharField(max_length=30, verbose_name='标签')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='本店价')
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='市场价')
    stock = models.IntegerField(default=0, verbose_name='库存')
    sales = models.IntegerField(default=0, verbose_name='销量')
    type = models.ForeignKey('Pro_Type', on_delete=models.CASCADE)
    comments = models.IntegerField(default=0, verbose_name='评价数')
    is_index = models.BooleanField(default=False, verbose_name='是否促销首页')
    is_putaway = models.BooleanField(default=True, verbose_name='是否上架销售')

    class Meta:
        db_table = 'Pro_sku'
        verbose_name = '商品SKU'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s: %s' % (self.id, self.name)


# 收藏表
class Collect(models.Model):
    pro_sku = models.ForeignKey(Pro_sku, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(UserInfo, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = '收藏管理'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "'%s' 由用户 '%s' 收藏" % (self.pro_sku.name, self.user.username)


# 商品评论表
# dis_pro : 评论的目标商品
# dis_content ：评论内容
# dis_user : 评论用户
class Pro_discass(models.Model):
    dis_pro = models.ForeignKey(Pro_sku, on_delete=models.CASCADE,verbose_name='评论商品')
    dis_content = models.CharField("评论内容",max_length=200)
    dis_user = models.ForeignKey(UserInfo, on_delete=models.CASCADE,verbose_name='评论用户')
    dis_time = models.DateField('评论日期', auto_now_add=True, null=True)
    dis_like = models.IntegerField('获赞数', default=0)

    class Meta:
        verbose_name = '评论表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "'%s'评论了'%s'" % (self.dis_user.username, self.dis_pro.name)


# 评论回复表
# reply_dis : 回复的目标评论
# reply_content : 回复内容
# reply_user ： 回复用户
class Reply_dis(models.Model):
    reply_dis = models.ForeignKey(Pro_discass, on_delete=models.CASCADE,verbose_name='回复评论')
    reply_content = models.CharField("回复内容",max_length=200)
    reply_user = models.ForeignKey( UserInfo, on_delete=models.CASCADE,verbose_name='回复用户')
    reply_time = models.DateField('回复日期', auto_now_add=True, null=True)
    reply_like = models.IntegerField('获赞数', default=0)

    class Meta:
        verbose_name = '回复表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "'%s'回复了'%s'" % (self.reply_user.username, self.reply_dis.dis_user.username)


class Group_buy(models.Model):
    '''
    商品团购表
    '''
    group_pro = models.ForeignKey(Pro_sku, on_delete=models.CASCADE)
    stime = models.DateTimeField(default='2019-9-8 15:30:30')
    ltime = models.DateTimeField(default='2019-10-10 15:30:30')

    class Meta:
        db_table = 'group_buy'
        verbose_name = '商品团购表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.group_pro.name
