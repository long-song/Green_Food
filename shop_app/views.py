from django.shortcuts import render, redirect, reverse, HttpResponse
from django.http import JsonResponse
from django.http import JsonResponse
from shop_app.models import *
from user_app.models import *
from user_app.views import login_required
import decimal


# Create your views here.
@login_required
def Orders(request):
    '''
    访问确认订单页面
    :param request:
    :return:
    '''
    pass



@login_required
def shopping_cart(request):
    if request.method == 'GET':
        uid = request.session['user_id']
        carts = CartInfo.objects.filter(user=uid)
        context = {
            'title': '购物车',
            'page_name': 1,
            'carts': carts
        }
        return render(request, 'shop_app/shopping_cart.html', context)
    if request.method == 'POST':
        user = request.session['user_id']
        sku_ids = request.POST.getlist('check')
        print(sku_ids)  # ['3', '1']
        if not sku_ids:
            return redirect(reverse('shopping_cart'))

        skus = []
        # 保存商品的总件数和总价格
        total_count = 0
        total_price = 0
        for sku_id in sku_ids:
            # 根据商品的id获取商品信息
            sku_id = int(sku_id)
            print(sku_id)
            sku = CartInfo.objects.get(id=sku_id)
            # # 获取用户所要购买的商品数量
            # count = conn.hget(cart_key, sku_id)
            # # 计算商品的小计
            # amount = sku.price * int(count)
            # # 动态给sku增加属性count,保存购买的商品数量
            # sku.count = int(count)
            # # 动态给sku增加属性amount,保存购买的商品小计
            # sku.amount = amount
            # 追加
            skus.append(sku)
            # 累加计算商品的总件数和总价格
            total_count += int(sku.ccount)
            total_price += sku.cprice
            # 运费：实际开发的时候属于一个子系统
        transit_price = 10  # 写死

        # 实付款
        total_pay = total_price + transit_price
        # 获取用户的收件地址
        uadress = Adress.objects.filter(user=user)

        # 组织上下文
        context = {
            'skus': skus,
            'total_count': total_count,
            'total_price': total_price,
            'transit_price': transit_price,
            'total_pay': total_pay,
            'uadress': uadress,
            'cart':'cart'
        }
        # print(locals())
        return render(request, 'shop_app/Orders.html',context)


@login_required
def add(request):
    uid = request.session['user_id']
    if request.method == 'POST':
        p_id = request.POST.get('p_id')
        count = request.POST.get('count')
        price = request.POST.get('price')
        print('p_id:', p_id, 'count:', count)
        # gid, count = int(gid), int(count)
        # 查询购物车中是否已经有此商品，如果有则数量增加，如果没有则新增
        carts = CartInfo.objects.filter(user_id=uid, pros=p_id)
        if carts:
            cart = carts[0]
            cart.ccount += int(count)
            print(cart.ccount, type(cart.ccount))
            print(price, type(price))
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


@login_required
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


@login_required
# 删除购物车记录
def delete(request, cart_id):
    print(cart_id)
    data = {}
    try:
        cart = CartInfo.objects.get(pk=int(cart_id))
        cart.pros_id = cart_id
        cart.delete()
        data['ok'] = 1
    except Exception:
        data['ok'] = 0
    return JsonResponse(data)

    # return render(request, 'shop_app/shopping_cart.html')
