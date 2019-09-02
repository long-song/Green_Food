# 自定义过滤器
# 过滤器的本质其实就是python中的函数
from django.template import Library
from user_app.models import Province, County, City

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
def province(num):
    '''
    将省份id转化为省份名
    :param num:
    :return:
    '''
    province_name = Province.objects.get(id=num)
    return province_name.province_name


@register.filter
def city(num):
    '''
    将城市id转化为城市名
    :param num:
    :return:
    '''
    city_name = City.objects.get(id=num)
    return city_name.city_name


@register.filter
def county(num):
    '''
    将区县id转化为区县名
    :param num:
    :return:
    '''
    county_name = County.objects.get(id=num)
    return county_name.county_name


@register.filter
def mod_val(str):
    '''
    将字符串以逗号分割
    并添加到列表
    显示前三个
    '''
    list = str.split(",")
    print(list)
    str1 = ''
    for i in list[:2]:
        str1 = str1+i
    return str1