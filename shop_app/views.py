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
        adress = request.POST.get('adress')
        pay_method = request.POST.get('pay_method')
        sku_ids = request.POST.get('sku_ids')  # 1,3
        count = request.POST.get('count')
        amount = request.POST.get('amount')
        # print(adress, type(adress), pay_method, type(pay_method), sku_ids, type(sku_ids), count, type(count),
        #       amount, type(amount))
        # 校验参数
        if not adress:
            return JsonResponse({'res': 1, 'errmsg': '请前往添加收货地址！'})
        if not pay_method:
            return JsonResponse({'res': 1, 'errmsg': '请前往选择支付方式！'})
        if not sku_ids:
            return JsonResponse({'res': 1, 'errmsg': '商品不存在'})

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


# 客户端的提交方式：post
# /order/pay
# 客户端传递的参数：order_id
def order_pay(request):
    """订单支付"""

    if request.method == 'POST':
        """
        去付款
        :param request:
        :return:
        """
        # 1.判断用户是否登录
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
        print('1')
        # 业务处理:使用python sdk调用支付宝的支付接口
        # 初始化
        alipay = AliPay(
            appid="2016101000649581",  # 应用id
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(settings.BASE_DIR, 'shop_app/app_private_key.pem'),
            alipay_public_key_path=os.path.join(settings.BASE_DIR, 'shop_app/alipay_public_key.pem'),
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
            notify_url=None
        )

        # 返回应答
        pay_url = 'https://openapi.alipaydev.com/gateway.do?' + order_string
        return JsonResponse({'res': 3, 'pay_url': pay_url})


# ajax post
# 前端传递的参数:订单id(order_id)
# /order/check
def Order_Check(request):
    """查询交易结果"""

    if request.method == 'POST':
        """
        查询交易结果
        :param request:
        :return:
        """
        # 1.判断用户是否登录
        user = request.session['user_id']
        user = UserInfo.objects.get(id=user)
        if not user:
            # 用户未登录
            return JsonResponse({'res': 0, 'errmsg': '用户未登录'})
        # 2.接收参数
        order_id = request.POST.get('order_id')
        # 3.校验参数
        if not order_id:
            return JsonResponse({'res': 1, 'errmsg': '无效的订单Id'})

        try:
            order = User_order.objects.get(order_id=order_id,
                                           user=user,
                                           pay_method=3,
                                           order_status=1)
        except User_order.DoesNotExist:
            return JsonResponse({'res': 2, 'errmsg': '订单不存在！'})

        # 4.业务处理：使用pythonsdk 调用支付宝的支付接口
        # 初始化
        alipay = AliPay(
            appid="2016101000649581",  # 使用沙箱的appid
            # appid="2016101602198783",# 使用真实环境的appid
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(settings.BASE_DIR, 'shop_app/app_private_key.pem'),
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_path=os.path.join(settings.BASE_DIR, 'shop_app/alipay_public_key.pem'),
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=True  # 默认False,当前是沙箱环境，改为True
            # debug=False # 默认False,当前是真实环境，改为False
        )

        # 调用支付宝交易查询接口
        while True:
            response = alipay.api_alipay_trade_query(order_id)
            """
             response = {
            "trade_no": "2017032121001004070200176844",
            "code": "10000",
            "invoice_amount": "20.00",
            "open_id": "20880072506750308812798160715407",
            "buyer_logon_id": "csq***@sandbox.com",
            "send_pay_date": "2017-03-21 13:29:17",
            "receipt_amount": "20.00",
            "out_trade_no": "out_trade_no15",
            "buyer_pay_amount": "20.00",
            "buyer_user_id": "2088102169481075",
            "msg": "Success",
            "point_amount": "0.00",
            "trade_status": "TRADE_SUCCESS",
            "total_amount": "20.00"
            }
            """
            code = response.get("code")
            if code == "10000" and response.get("trade_status") == "TRADE_SUCCESS":
                # 支付成功
                # 获取支付宝交易号
                trade_no = response.get('trade_no')
                # 更新订单状态
                order.trade_no = trade_no
                order.order_status = 4  # 待评价
                order.save()
                # 返回结果
                return JsonResponse({'res': 3, 'message': '支付成功'})
            elif code == "40004" or (code == "10000" and response.get("trade_status") == "WAIT_BUYER_PAY"):
                # 等待买家付款
                # 40004：业务处理失败，可能一会就会成功
                import time
                time.sleep(5)
                continue
            else:
                # 支付出错
                print('code=', code)
                return JsonResponse({'res': 4, 'errmsg': '支付失败'})


# /order/comment
@login_required
def order_comment(request, order_id):
    """评论视图"""

    if request.method == 'GET':
        """
        显示评论页面
        :param request:
        :return:
        """
        # 校验数据
        user = request.session['user_id']
        user = UserInfo.objects.get(id=user)
        if not order_id:
            return redirect(reverse('user'))

        try:
            order = User_order.objects.get(order_id=order_id, user=user)
        except User_order.DoesNotExist:
            return redirect(reverse('user'))

        # 根据订单的状态获取订单的状态标题
        order.status_name = User_order.ORDER_STATUS[order.order_status]
        # 获取订单商品信息
        order_skus = Order.objects.filter(order_id=order_id)
        order.order_skus = order_skus

        # 使用模板
        return render(request, "user_app/order_comment.html", {"order": order})

    if request.method == 'POST':
        """
        提交用户评论的内容
        :param request:
        :return:
        """
        user = request.user
        # 校验数据
        if not order_id:
            return redirect(reverse('user:order'))

        try:
            order = User_order.objects.get(order_id=order_id, user=user)
        except User_order.DoesNotExist:
            return redirect(reverse("user:order"))

        # 获取评论条数
        total_count = request.POST.get("total_count")
        total_count = int(total_count)

        # 循环获取订单中商品的评论内容
        for i in range(1, total_count + 1):
            # 获取评论的商品的id
            sku_id = request.POST.get("sku_%d" % i)  # sku_1 sku_2
            # 获取评论的商品的内容
            content = request.POST.get('content_%d' % i, '')  # cotent_1 content_2 content_3
            try:
                order_goods = User_order.objects.get(order=order, sku_id=sku_id)
            except User_order.DoesNotExist:
                continue

            order_goods.comment = content
            order_goods.save()

        order.order_status = 5  # 已完成
        order.save()

        return redirect(reverse("user", kwargs={"page": 1}))


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
