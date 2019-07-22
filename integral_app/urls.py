from django.contrib import admin
from django.urls import path, include
from integral_app import views

urlpatterns = [
    path('group_buy/', views.group_buy, name='group_buy'),  # 访问今日团购活动页面
    path('integral/', views.integral, name='integral'),  # 访问所有果蔬页面
    path('products/', views.products, name='products'),  # 访问水果馆活动页面
    path('products_list/', views.products_list, name='products_list'),  # 访问蔬菜馆页面
    path('product_detailed/', views.product_detailed, name='product_detailed'),  # 访问商品详情页面
]
