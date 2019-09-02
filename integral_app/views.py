from django.shortcuts import render, redirect
from shop_app.models import *
from common.data_page import pagination
from integral_app.models import Collect,Group_buy
import random

# 在发送ajax的post请求时解决跨网站请求
from django.views.decorators.csrf import csrf_exempt


# Create your views here.

def group_buy(request):
    '''
    访问今日团购活动页面
    :param request:
    :return:
    '''
    # 左侧
    g_ids = Group_buy.objects.values_list('group_pro', flat=True)
    selected_name = random.sample(list(g_ids), 5)
    g_id = Group_buy.objects.filter(group_pro__in=selected_name)

    # 右上侧
    selected_name = random.sample(list(g_ids), 1)
    p_id = Group_buy.objects.filter(group_pro__in=selected_name)

    # 右下侧
    selected_name = random.sample(list(g_ids), 4)
    c_id = Group_buy.objects.filter(group_pro__in=selected_name)

    # 获取时间
    time = Group_buy.objects.all()
    # print(time)

    return render(request, 'integral_app/Group_buy.html', {'group_buy':'group_buy',"g_id": g_id, "p_id": p_id, "c_id": c_id, "time": time})


def integral(request):
    '''
    访问所有果蔬页面
    :param request:
    :return:
    '''
    page = int(request.GET.get('page'))
    # print(page,type(page))
    own = Pro_sku.objects.all().exclude(is_index=True)
    data_page, pages = pagination(own, page_size=8, page=page, page_type=1)
    print(data_page, pages)
    return render(request, 'integral_app/integral.html',
                  {'integral': 'integral', 'own': own, 'data_page': data_page, 'pages': pages})


def products(request):
    '''
    访问水果馆页面
    :param request:
    :return:
    '''
    page = int(request.GET.get('page'))
    fruits = Pro_sku.objects.filter(type=1,is_index=False)
    print(fruits)
    data_page, pages = pagination(fruits, page_size=8, page=page, page_type=2)
    return render(request, 'integral_app/Products.html',
                  {'products': 'products', 'fruits': fruits, 'data_page': data_page, 'pages': pages})


def products_list(request):
    '''
    访问蔬菜馆页面
    :param request:
    :return:
    '''
    page = int(request.GET.get('page'))
    vegetables = Pro_sku.objects.filter(type=2,is_index=False)
    data_page, pages = pagination(vegetables, page_size=8, page=page, page_type=1)
    return render(request, 'integral_app/Product-List.html',
                  {'products_list': 'products_list', 'vegetables': vegetables, 'data_page': data_page, 'pages': pages})


def product_detailed(request):
    '''
    访问商品详情页面
    :param request:
    :return:
    '''
    if request.method == 'GET':
        sales = Pro_sku.objects.all().order_by('-sales')
        sku_id = request.GET.get("id")
        sku = Pro_sku.objects.get(id=sku_id)
        collect = Collect.objects.filter(pro_sku=sku_id)
        if collect:
            return render(request, 'integral_app/Product-detailed.html',
                          {'sales': sales[:5], 'sku': sku, 'p_id': sku_id, 'fav': 'fav'})
        else:
            return render(request, 'integral_app/Product-detailed.html',
                          {'sales': sales[:5], 'sku': sku, 'p_id': sku_id})
