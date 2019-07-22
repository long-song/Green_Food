from django.shortcuts import render


# Create your views here.

def group_buy(request):
    '''
    访问今日团购活动页面
    :param request:
    :return:
    '''
    return render(request, 'integral_app/Group_buy.html')


def integral(request):
    '''
    访问所有果蔬页面
    :param request:
    :return:
    '''
    return render(request, 'integral_app/integral.html')


def products(request):
    '''
    访问水果馆页面
    :param request:
    :return:
    '''
    return render(request, 'integral_app/Products.html')


def products_list(request):
    '''
    访问蔬菜馆页面
    :param request:
    :return:
    '''
    return render(request, 'integral_app/Product-List.html')


def product_detailed(request):
    '''
    访问商品详情页面
    :param request:
    :return:
    '''
    return render(request, 'integral_app/Product-detailed.html')
