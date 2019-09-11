from django.contrib import admin
from django.urls import path, include
from shop_app import views
from django.conf.urls import url

urlpatterns = [
    path('Orders/', views.Orders, name='Orders'),  # 访问购物车确认订单页面
    path('Orders_one/', views.Orders_one, name='Orders_one'),  # 访问单个产品确认订单页面
    path('shopping_cart/', views.shopping_cart, name='shopping_cart'),  # 访问购物车页面
    path('add/',views.add, name="add"),
    url(r'^edit(\d+)_(\d+)/$', views.edit, name="edit"),
    url(r'^delete(\d+)/$', views.delete, name="delete"),

]
