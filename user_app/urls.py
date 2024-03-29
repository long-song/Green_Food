from django.contrib import admin
from django.urls import path, include
from user_app import views

urlpatterns = [
    path('index/', views.index, name='index'),  # 访问首页路由
    path('login/', views.login, name='login'),  # 访问登录界面路由
    path('phone_code/', views.phone_code, name='phone_code'), # 获取手机号发送验证码
    path('registered/', views.registered, name='registered'),  # 访问注册界面路由
    path('logout/', views.logout, name='logout'),  # 访问注销路由
    path('captcha/', include('captcha.urls')),  # 访问验证码路由
    path('user/', views.user, name='user'),  # 访问我的订单路由
    path('user_info/', views.user_info, name='user_info'),  # 访问个人信息路由
    path('user_password/', views.user_password, name='user_password'),  # 访问修改密码路由
    path('user_collect/', views.user_collect, name='user_collect'),  # 访问我的收藏路由
    path('user_address/', views.user_address, name='user_address'),  # 访问收货地址管理路由
    path('user_info_set/', views.user_info_set, name='user_info_set'),  # 访问收货地址管理路由
    path('new_head/', views.new_head, name='new_head'),  # 修改头像路由
    path('user_address_add/', views.user_address_add, name='user_address_add'),  # 访问增加收货地址
    path('user_address_delete/<int:id>/', views.user_address_delete, name='user_address_delete'),
    path('user_address_change/<int:id>', views.user_address_change, name='user_address_change')
]
