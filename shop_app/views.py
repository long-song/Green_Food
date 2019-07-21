from django.shortcuts import render

# Create your views here.

def Orders(request):
    '''
    访问确认订单页面
    :param request:
    :return:
    '''
    return render(request, 'shop_app/Orders.html')

def shopping_cart(request):
    '''
    访问购物车页面
    :param request:
    :return:
    '''
    return render(request, 'shop_app/shopping_cart.html')