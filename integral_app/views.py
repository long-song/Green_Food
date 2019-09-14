from django.http import JsonResponse
from django.shortcuts import render, redirect
from shop_app.models import *
from common.data_page import pagination
from integral_app.models import Collect, Group_buy, Pro_discass,Reply_dis
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

    return render(request, 'integral_app/Group_buy.html',
                  {'group_buy': 'group_buy', "g_id": g_id, "p_id": p_id, "c_id": c_id, "time": time})


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
    fruits = Pro_sku.objects.filter(type=1, is_index=False)
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
    vegetables = Pro_sku.objects.filter(type=2, is_index=False)
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
        # 获取信息
        user = request.session['user_id']
        user = UserInfo.objects.get(id=user)
        # 获取销量排行
        sales = Pro_sku.objects.all().order_by('-sales')
        # 获取产品
        sku_id = request.GET.get("id")
        sku = Pro_sku.objects.get(id=sku_id)
        # 查看是否收藏
        collect = Collect.objects.filter(user=user, pro_sku=sku_id)
        # 获取评论
        sku_comment = Pro_discass.objects.filter(dis_pro=sku).order_by('-dis_like')
        context = {'sales': sales[:5],
                   'sku': sku,
                   'p_id': sku_id,
                   'user': user}
        # 如果有收藏则添加fav参数
        if collect:
            context.update({'fav': 'fav'})
        # 如果有评价则添加评价信息
        if sku_comment:
            context.update({'sku_comment': sku_comment[:10],'comment_len':len(sku_comment)})
        return render(request, 'integral_app/Product-detailed.html', context)

    if request.method == 'POST':
        # 产品id
        sku_id = request.POST.get('sku_id')
        # 用户id
        uid = request.session['user_id']
        # 数量
        count = request.POST.get('number')
        # 当前产品
        order = Pro_sku.objects.get(id=sku_id)
        # 金额
        total_price = order.price * int(count)
        # 运费
        transit_price = 10
        # 实付款
        total_pay = total_price + transit_price
        # 获取默认地址，如果没有则重定向到添加地址页面
        try:
            uadress = Adress.objects.filter(user=uid)
        except:
            return redirect('user_address_add')
        # 组织上下文
        context = {
            'order': order,
            'total_count': count,
            'total_price': total_price,
            'transit_price': transit_price,
            'total_pay': total_pay,
            'uadress': uadress,
            'uid': 'uid'
        }
        return render(request, 'shop_app/Orders.html', context)


def dis_comment(request):
    '''
    产品评论
    :param request:
    :return:
    '''
    if request.method == 'POST':
        # 判断用户是否登录
        user = request.session['user_id']
        user = UserInfo.objects.get(id=user)
        if not user:
            # 用户未登录
            return JsonResponse({'res': 0, 'errmsg': '用户未登录'})

        # 接收参数
        sku_id = request.POST.get('sku_id')
        comment = request.POST.get('comment')

        # 检验数据
        if not all([sku_id, comment]):
            return JsonResponse({'res': 1, 'errmsg': '数据不完整'})

        try:
            sku = Pro_sku.objects.get(id=sku_id)
        except:
            return JsonResponse({'res': 2, 'errmsg': '产品不存在'})

        # 完成核心业务：
        Pro_discass.objects.create(dis_pro=sku, dis_user=user, dis_content=comment)

        return JsonResponse({'res': 3, 'message': '评论成功'})

def reply_comment(request):
    '''
    产品评论
    :param request:
    :return:
    '''
    if request.method == 'POST':
        # 判断用户是否登录
        user = request.session['user_id']
        user = UserInfo.objects.get(id=user)
        if not user:
            # 用户未登录
            return JsonResponse({'res': 0, 'errmsg': '用户未登录'})

        # 接收参数
        reply_dis = request.POST.get('reply_dis')
        comment = request.POST.get('comment')

        # 检验数据
        if not all([reply_dis, comment]):
            return JsonResponse({'res': 1, 'errmsg': '数据不完整'})

        try:
            reply_dis = Pro_discass.objects.get(id=reply_dis)
        except:
            return JsonResponse({'res': 2, 'errmsg': '此评论不存在'})

        # 完成核心业务：
        Reply_dis.objects.create(reply_dis=reply_dis,reply_content=comment,reply_user=user)

        return JsonResponse({'res': 3, 'message': '回复成功'})
