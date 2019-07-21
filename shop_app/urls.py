from django.contrib import admin
from django.urls import path,include
from shop_app import views

urlpatterns = [
    path('user_app/', include('user_app.urls')),  # 添加user_app的urls
    path('integral_app/', include('integral_app.urls')),  # 添加integral_app的urls
    path('Orders/', views.Orders,name='Orders'),  # 访问确认订单页面
    path('shopping_cart/', views.shopping_cart,name='shopping_cart'),  # 访问购物车页面
]