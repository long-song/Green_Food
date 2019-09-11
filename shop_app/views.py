from django.db import transaction
from django.shortcuts import render, redirect, reverse, HttpResponse
from django.http import JsonResponse
from shop_app.models import *
from user_app.models import *
from user_app.views import login_required
import decimal
from django.conf import settings
from datetime import datetime
from alipay import AliPay
import os


@login_required
@transaction.atomic
def Orders_one(request):
    '''
    访问确认订单页面
    :param request:
    :return:
    '''
    if request.method == 'POST':
        '''订单创建'''
        # 判断用户是否登录
        user = request.session['user_id']
        user = UserInfo.objects.get(id=user)
        if not user:
            # 用户未登录
            return JsonResponse({'res': 0, 'errmsg': '用户未登录'})

        # 接收参数
        adress = int(request.POST.get('adress'))
        pay_method = request.POST.get('pay_method')
        sku_ids = request.POST.get('sku_ids')  # 1,3
        count = request.POST.get('count')
        amount = request.POST.get('amount')
        print(adress, type(adress), pay_method, type(pay_method), sku_ids, type(sku_ids), count, type(count),
              amount, type(amount))
        # 校验参数
        if not all([adress, pay_method, sku_ids]):
            return JsonResponse({'res': 1, 'errmsg': '参数不完整'})

        # 校验支付方式
        if pay_method not in User_order.PAY_METHODS.keys():
            return JsonResponse({'res': 2, 'errmsg': '非法的支付方式'})

        # 校验地址
        try:
            addr = Adress.objects.get(id=adress)
        except Adress.DoesNotExist:
            # 地址不存在
            return JsonResponse({'res': 3, 'errmsg': '地址非法'})

        # 创建订单核心业务

        # 组织参数
        # 订单id: 20171122181630+用户id
        order_id = datetime.now().strftime('%Y%m%d%H%M%S') + str(user.id)
        # 运费
        transit_price = 10

        # 总数目和总金额
        total_count = int(count)
        total_price = float(amount)

        # 设置事务保存点
        print('0')
        save_id = transaction.savepoint()
        try:
            # 向df_order_info表中添加一条记录
            order = User_order.objects.create(order_id=order_id,
                                              user=user,
                                              adress=addr,
                                              pay_method=pay_method,
                                              total_count=total_count,
                                              total_price=total_price,
                                              transit_price=transit_price)
            # 用户的订单中有几个商品，需要向df_order_goods表中加入几条记录
            for i in range(3):
                # 获取商品的信息
                try:
                    sku_id = int(sku_ids)
                    sku = Pro_sku.objects.get(id=sku_id)
                except:
                    # 商品不存在
                    transaction.savepoint_rollback(save_id)
                    return JsonResponse({'res': 4, 'errmsg': '商品不存在'})

                # 判断商品的库存
                if total_count > sku.stock:
                    transaction.savepoint_rollback(save_id)
                    return JsonResponse({'res': 6, 'errmsg': '商品库存不足'})

                # 更新商品的库存和销量
                orgin_stock = sku.stock
                new_stock = orgin_stock - total_count
                new_sales = sku.sales + total_count

                # 返回受影响的行数
                res = Pro_sku.objects.filter(id=sku_id, stock=orgin_stock).update(stock=new_stock, sales=new_sales)
                if res == 0:
                    if i == 2:
                        # 尝试的第3次
                        transaction.savepoint_rollback(save_id)
                        return JsonResponse({'res': 7, 'errmsg': '下单失败2'})
                    continue

                # 向df_order_goods表中添加一条记录
                Order.objects.create(order=order,
                                     pro_id=sku,
                                     count=total_count,
                                     prices=total_price)
                # 跳出循环
                break
        except Exception as e:
            transaction.savepoint_rollback(save_id)
            return JsonResponse({'res': 7, 'errmsg': '下单失败'})

        #
        # 提交事务
        transaction.savepoint_commit(save_id)

        # 返回应答
        return JsonResponse({'res': 5, 'message': '创建成功'})


# Create your views here.
@login_required
@transaction.atomic
def Orders(request):
    '''
    访问确认订单页面
    :param request:
    :return:
    '''
    if request.method == 'POST':
        '''订单创建'''
        # 判断用户是否登录
        user = request.session['user_id']
        user = UserInfo.objects.get(id=user)
        if not user:
            # 用户未登录
            return JsonResponse({'res': 0, 'errmsg': '用户未登录'})

        # 接收参数
        adress = int(request.POST.get('adress'))
        pay_method = request.POST.get('pay_method')
        sku_ids = request.POST.get('sku_ids')  # 1,3
        count = request.POST.get('count')
        amount = request.POST.get('amount')
        # print(adress, type(adress), pay_method, type(pay_method), sku_ids, type(sku_ids), count, type(count),
        #       amount, type(amount))
        # 校验参数
        if not all([adress, pay_method, sku_ids]):
            return JsonResponse({'res': 1, 'errmsg': '参数不完整'})

        # 校验支付方式
        if pay_method not in User_order.PAY_METHODS.keys():
            return JsonResponse({'res': 2, 'errmsg': '非法的支付方式'})

        # 校验地址
        try:
            addr = Adress.objects.get(id=adress)
        except Adress.DoesNotExist:
            # 地址不存在
            return JsonResponse({'res': 3, 'errmsg': '地址非法'})

        # 创建订单核心业务

        # 组织参数
        # 订单id: 20171122181630+用户id
        order_id = datetime.now().strftime('%Y%m%d%H%M%S') + str(user.id)
        # 运费
        transit_price = 10

        # 总数目和总金额
        total_count = 0
        total_price = 0

        # 设置事务保存点
        print('0')
        save_id = transaction.savepoint()
        try:
            # 向df_order_info表中添加一条记录
            order = User_order.objects.create(order_id=order_id,
                                              user=user,
                                              adress=addr,
                                              pay_method=pay_method,
                                              total_count=total_count,
                                              total_price=total_price,
                                              transit_price=transit_price)
            # 用户的订单中有几个商品，需要向df_order_goods表中加入几条记录

            sku_ids = sku_ids.split(',')
            count = count.split(',')
            amount = amount.split(',')

            for j, sku_id in enumerate(sku_ids):
                for i in range(3):
                    # 获取商品的信息
                    try:
                        sku_id = int(sku_id)
                        cart = CartInfo.objects.get(id=sku_id)
                        sku_id = cart.pros.id
                        sku = Pro_sku.objects.get(id=sku_id)
                    except:
                        # 商品不存在
                        transaction.savepoint_rollback(save_id)
                        return JsonResponse({'res': 4, 'errmsg': '商品不存在'})

                    # 从redis中获取用户所要购买的商品的数量
                    # count = conn.hget(cart_key, sku_id)

                    # 判断商品的库存
                    count1 = count[j]
                    prices = amount[j]
                    if int(count1) > sku.stock:
                        transaction.savepoint_rollback(save_id)
                        return JsonResponse({'res': 6, 'errmsg': '商品库存不足'})

                    # 更新商品的库存和销量
                    orgin_stock = sku.stock
                    new_stock = orgin_stock - int(count1)
                    new_sales = sku.sales + int(count1)

                    # print('user:%d times:%d stock:%d' % (user.id, i, sku.stock))
                    # import time
                    # time.sleep(10)

                    # update df_goods_sku set stock=new_stock, sales=new_sales
                    # where id=sku_id and stock = orgin_stock

                    # 返回受影响的行数
                    res = Pro_sku.objects.filter(id=sku_id, stock=orgin_stock).update(stock=new_stock, sales=new_sales)
                    if res == 0:
                        if i == 2:
                            # 尝试的第3次
                            transaction.savepoint_rollback(save_id)
                            return JsonResponse({'res': 7, 'errmsg': '下单失败2'})
                        continue

                    # 向df_order_goods表中添加一条记录
                    Order.objects.create(order=order,
                                         pro_id=sku,
                                         count=count1,
                                         prices=prices)

                    # 累加计算订单商品的总数量和总价格
                    total_count += int(count1)
                    total_price += float(prices)

                    # 跳出循环
                    break

            # 更新订单信息表中的商品的总数量和总价格
            order.total_count = total_count
            order.total_price = total_price
            order.save()
        except Exception as e:
            transaction.savepoint_rollback(save_id)
            return JsonResponse({'res': 7, 'errmsg': '下单失败'})

        # 提交事务
        transaction.savepoint_commit(save_id)

        # 清除用户购物车中对应的记录
        for cart_id in sku_ids:
            cart = CartInfo.objects.get(pk=int(cart_id))
            # cart.pros_id = cart_id
            cart.delete()
        #
        # 返回应答
        return JsonResponse({'res': 5, 'message': '创建成功'})


# ajax post
# 前端传递的参数:订单id(order_id)
# /order/pay
def Order_Pay(request):
    '''订单支付'''
    if request.method == 'POST':
        '''订单支付'''
        # 用户是否登录
        user = request.session['user_id']
        user = UserInfo.objects.get(id=user)
        if not user:
            # 用户未登录
            return JsonResponse({'res': 0, 'errmsg': '用户未登录'})

        # 接收参数
        order_id = request.POST.get('order_id')

        # 校验参数
        if not order_id:
            return JsonResponse({'res': 1, 'errmsg': '无效的订单id'})

        try:
            order = User_order.objects.get(order_id=order_id,
                                           user=user,
                                           pay_method=3,
                                           order_status=1)
        except User_order.DoesNotExist:
            return JsonResponse({'res': 2, 'errmsg': '订单错误'})

        # 业务处理:使用python sdk调用支付宝的支付接口
        # 初始化
        alipay = AliPay(
            appid="2016090800464054",  # 应用id
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(settings.BASE_DIR, 'apps/order/app_private_key.pem'),
            alipay_public_key_path=os.path.join(settings.BASE_DIR, 'apps/order/alipay_public_key.pem'),
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=True  # 默认False
        )

        # 调用支付接口
        # 电脑网站支付，需要跳转到https://openapi.alipaydev.com/gateway.do? + order_string
        total_pay = order.total_price + order.transit_price  # Decimal
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,  # 订单id
            total_amount=str(total_pay),  # 支付总金额
            subject='浦江食品商城%s' % order_id,
            return_url=None,
            notify_url=None  # 可选, 不填则使用默认notify url
        )

        # 返回应答
        pay_url = 'https://openapi.alipaydev.com/gateway.do?' + order_string
        return JsonResponse({'res': 3, 'pay_url': pay_url})


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
        count_list = request.POST.getlist('count')
        prices = request.POST.getlist('cprice')
        print(sku_ids, count_list, prices)  # ['3', '1']
        if not sku_ids:
            return redirect(reverse('shopping_cart'))

        skus = []
        cart_ids = []
        # 保存商品的总件数和总价格
        total_count = 0
        total_price = 0
        for i, sku_id in enumerate(sku_ids):
            # 根据商品的id获取商品信息
            sku_id = int(sku_id)
            sku = CartInfo.objects.get(id=sku_id)
            # # 获取用户所要购买的商品数量
            # count = conn.hget(cart_key, sku_id)
            # 计算商品的小计
            amount = sku.pros.price * int(count_list[i])
            # 动态给sku增加属性count,保存购买的商品数量
            sku.count = int(count_list[i])
            # 动态给sku增加属性amount,保存购买的商品小计
            sku.amount = amount
            # 追加
            skus.append(sku)
            cart_ids.append(str(sku.pros.id))
            # 累加计算商品的总件数和总价格
            total_count += int(sku.count)
            total_price += sku.amount
            # 运费：实际开发的时候属于一个子系统
        transit_price = 10  # 写死

        # 实付款
        total_pay = total_price + transit_price
        # 获取用户的收件地址
        uadress = Adress.objects.filter(user=user)

        # 组织上下文
        sku_ids = ','.join(sku_ids)
        count_list = ','.join(count_list)
        prices = ','.join(prices)
        # cart_ids = ','.join(cart_ids)
        context = {
            'skus': skus,
            'sku_ids': sku_ids,
            'count_list': count_list,
            'amount': prices,
            # 'cart_ids':sku_ids,
            'total_count': total_count,
            'total_price': total_price,
            'transit_price': transit_price,
            'total_pay': total_pay,
            'uadress': uadress,
            'cart': 'cart'
        }
        return render(request, 'shop_app/Orders.html', context)


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
        return JsonResponse({'message': message})


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
