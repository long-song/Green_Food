from django.contrib import admin
from django.urls import path, include
from shop_app import views

urlpatterns = [
    path('Orders/', views.Orders, name='Orders'),  # 访问确认订单页面
    path('shopping_cart/', views.shopping_cart, name='shopping_cart'),  # 访问购物车页面

]
