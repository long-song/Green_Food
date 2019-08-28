from django.shortcuts import render,redirect
from integral_app.models import *
from shop_app.models import *
from user_app.models import *
from common.data_page import pagination
# 在发送ajax的post请求时解决跨网站请求
from django.views.decorators.csrf import csrf_exempt


# Create your views here.

def group_buy(request):
    '''
    访问今日团购活动页面
    :param request:
    :return:
    '''
    return render(request, 'integral_app/Group_buy.html',{'group_buy':'group_buy'})


def integral(request):
    '''
    访问所有果蔬页面
    :param request:
    :return:
    '''
    page = int(request.GET.get('page'))
    # print(page,type(page))
    own = Pro_sku.objects.all()
    data_page,pages = pagination(own,page_size=8,page=page,page_type=1)
    print(data_page,pages)
    return render(request, 'integral_app/integral.html', {'integral':'integral','own': own,'data_page':data_page,'pages':pages})


def products(request):
    '''
    访问水果馆页面
    :param request:
    :return:
    '''
    page = int(request.GET.get('page'))
    fruits = Pro_sku.objects.exclude(type_id=2)
    data_page, pages = pagination(fruits, page_size=8, page=page, page_type=1)
    return render(request, 'integral_app/Products.html', {'products':'products','fruits': fruits,'data_page':data_page,'pages':pages})


def products_list(request):
    '''
    访问蔬菜馆页面
    :param request:
    :return:
    '''
    page = int(request.GET.get('page'))
    vegetables = Pro_sku.objects.exclude(type_id=1)
    data_page, pages = pagination(vegetables, page_size=8, page=page, page_type=1)
    return render(request, 'integral_app/Product-List.html', {'products_list':'products_list','vegetables': vegetables,'data_page':data_page,'pages':pages})


def product_detailed(request):
    '''
    访问商品详情页面
    :param request:
    :return:
    '''
    sales = Pro_sku.objects.filter().order_by('-sales')
    addres_id = request.GET.get("id")
    fav0 = request.GET.get('fav')
    detail_all = Pro_sku.objects.filter(id=addres_id)
    if request.session.has_key('is_login'):
        a = request.session['user_id']
        col = Collect.objects.filter(user=a, pro_id=addres_id)
        if fav0 == "0":
            col.delete()
            return render(request, 'integral_app/Product-detailed.html',
                          {'sales': sales[:5], 'detail_all': detail_all, 'p_id': addres_id})
        if col:
            fav = "已收藏"
            return render(request, 'integral_app/Product-detailed.html',
                          {'sales': sales[:5], 'detail_all': detail_all, 'p_id': addres_id,'fav':fav})
    return render(request, 'integral_app/Product-detailed.html', {'sales': sales[:5], 'detail_all': detail_all,'p_id':addres_id})


