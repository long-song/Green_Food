from django.shortcuts import render,redirect,reverse
from django.http import JsonResponse
from django.db import transaction
from datetime import datetime
# from user_app import user_decorator
from integral_app.models import *
from user_app.models import *
from shop_app.models import *
import decimal



# Create your views here.

def Orders(request):
    '''
    访问确认订单页面
    :param request:
    :return:
    '''
    if request.method=='POST':
        info = request.POST.get('price')
        num = request.POST.get('num')
        oprice = request.POST.get('oprice')
        p_id = request.POST.get('p_id')
        print('单价=',info,'数量=',num,'总价=',oprice,'id=',p_id)
        return render(request, 'shop_app/Orders.html',locals())
    return render(request, 'shop_app/Orders.html')


# @user_decorator.login
def shopping_cart(request):
    if request.method == 'GET':
        uid = request.session['user_id']
        carts = CartInfo.objects.filter(user=uid)
        context = {
            'title': '购物车',
            'page_name': 1,
            'carts': carts
        }
        # if request.is_ajax():
        #     count = CartInfo.objects.filter(user_id=request.session['user_id']).count()
        #     # 求当前用户购买了几件商品
        #     return JsonResponse({'count': count})
        return render(request, 'shop_app/shopping_cart.html', context)


# @user_decorator.login
def add(request):
    uid = request.session['user_id']
    if request.method == 'POST':
        p_id = request.POST.get('p_id')
        count = request.POST.get('count')
        price = request.POST.get('price')
        print('p_id:',p_id,'count:',count)
        # gid, count = int(gid), int(count)
        # 查询购物车中是否已经有此商品，如果有则数量增加，如果没有则新增
        carts = CartInfo.objects.filter(user_id=uid, pros=p_id)
        if carts:
            cart = carts[0]
            cart.ccount += int(count)
            print(cart.ccount,type(cart.ccount))
            print(price,type(price))
            cart.cprice += decimal.Decimal(price)
            message = 'OK'
            print(1)
        else:
            cart = CartInfo()
            cart.user_id = uid
            cart.pros_id = p_id
            cart.ccount = count
            cart.cprice = price
            message = 'OK'
            print(2)
        cart.save()
        # # 如果是ajax提交则直接返回json，否则转向购物车
        # if request.is_ajax():
        #     count = CartInfo.objects.filter(user_id=request.session['user_id']).count()
        #     # 求当前用户购买了几件商品
        return JsonResponse({'message': message})
    # else:
    #     return redirect(reverse("shop_app:cart"))


# @user_decorator.login
def edit(request, cart_id, count):
    data = {}
    try:
        cart = CartInfo.objects.get(pk=int(cart_id))
        cart.count = int(count)
        cart.save()
        data['count'] = 0
    except Exception:
        data['count'] = count
    return JsonResponse(data)


# @user_decorator.login
def delete(request, cart_id):
    data = {}
    try:
        cart = CartInfo.objects.get(pk=int(cart_id))
        cart.delete()
        data['ok'] = 1
    except Exception:
        data['ok'] = 0
    return JsonResponse(data)

    # return render(request, 'shop_app/shopping_cart.html')