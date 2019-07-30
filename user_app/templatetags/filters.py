# 自定义过滤器
# 过滤器的本质其实就是python中的函数
from django.template import Library

# 创建一个library类的对象
register = Library()

# 自定义过滤器至少有一个参数，最多2个
@register.filter  # 将函数装饰成python中的过滤器进行使用
def mod(num):
    '''
    将1,2转换为男女
    :param num:
    :return:
    '''
    if num == 1:
        return '男'
    else:
        return '女'


@register.filter
def mod_val(num,val):
    '''判断num是否能被val整除'''
    return num % val == 0
