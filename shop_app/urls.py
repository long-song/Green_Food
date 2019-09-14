from django.contrib import admin
from django.urls import path, include
from shop_app import views
from django.conf.urls import url

urlpatterns = [
    path('Orders/', views.Orders, name='Orders'),  # 访问购物车确认订单页面
    path('Orders_one/', views.Orders_one, name='Orders_one'),  # 访问单个产品确认订单页面
    url(r'^pay$', views.order_pay, name='order_pay'),  # 订单支付
    path('check/', views.Order_Check, name="order_check"),  # 订单交易查询的路由
    path('comment/<int:order_id>',views.order_comment, name="order_comment"),  # 订单评论的路由

    path('shopping_cart/', views.shopping_cart, name='shopping_cart'),  # 访问购物车页面
    path('add/', views.add, name="add"),
    url(r'^edit(\d+)_(\d+)/$', views.edit, name="edit"),
    url(r'^delete(\d+)/$', views.delete, name="delete"),

]
