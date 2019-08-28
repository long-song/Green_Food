from django.shortcuts import render,redirect,reverse,HttpResponse
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
    if request.method == 'GET':
        p_id = request.GET.get('p_id')
        uid = request.session['user_id']
        order = Pro_sku.objects.get(id=p_id)
        # 获取默认地址，如果没有则重定向到添加地址页面
        try:
            uadress = Adress.objects.get(user=uid,is_default=True)
        except:
            return redirect('user_address_add')
        return render(request, 'shop_app/Orders.html', locals())



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
        # if request.is_ajax():
        #     count = CartInfo.objects.filter(user_id=request.session['user_id']).count()
        #     # 求当前用户购买了几件商品
        #     return JsonResponse({'count': count})
        return render(request, 'shop_app/shopping_cart.html', context)


@login_required
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
        cart.pros_id=cart_id
        cart.delete()
        data['ok'] = 1
    except Exception:
        data['ok'] = 0
    return JsonResponse(data)

    # return render(request, 'shop_app/shopping_cart.html')