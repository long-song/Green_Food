from django.shortcuts import render


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


def shopping_cart(request):
    '''
    访问购物车页面
    :param request:
    :return:
    '''
    return render(request, 'shop_app/shopping_cart.html')
