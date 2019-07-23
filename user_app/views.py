from django.shortcuts import render, redirect, HttpResponse
from user_app.models import UserInfo
from user_app.froms import UserForm, RegisterForm
import datetime


# Create your views here.
def index(request):
    '''
    访问首页
    :param request:
    :return:
    '''
    print("获取请求方式：", request.method)
    print("获取访问路径：", request.path)
    return render(request, 'index.html')


def login(request):
    '''
        访问登录页面
        :param request:
        :return:
        '''
    if request.session.get('is_login', None):
        return redirect('index')
    if request.method == "POST":
        login_form = UserForm(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            try:
                user = UserInfo.objects.get(username=username)
                if user.password == password:
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_username'] = user.username
                    return redirect('index')
                else:
                    message = "密码不正确！"
            except:
                message = "用户不存在！"
        return render(request, 'user_app/Login.html', locals())
    else:
        login_form = UserForm()
        return render(request, 'user_app/Login.html', locals())


def registered(request):
    '''
    访问注册页面
    :param request:
    :return:
    '''
    if request.session.get('is_login', None):
        # 登录状态不允许注册。你可以修改这条原则！
        return redirect("index")
    if request.method == "POST":
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():  # 获取数据
            username = register_form.cleaned_data['username']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            phone = register_form.cleaned_data['phone']
            # email = register_form.cleaned_data['email']
            # sex = register_form.cleaned_data['sex']
            if password1 != password2:  # 判断两次密码是否相同
                message = "两次输入的密码不同！"
                return render(request, 'user_app/registered.html', locals())
            else:
                same_name_user = UserInfo.objects.filter(username=username)
                if same_name_user:  # 用户名唯一
                    message = '用户已经存在，请重新选择用户名！'
                    return render(request, 'user_app/registered.html', locals())
                else:
                    same_phone_user = UserInfo.objects.filter(phone=None)
                    if same_phone_user:  # 手机号唯一
                        message = '该手机号已被注册，请使用别的手机号！'
                        return render(request, 'user_app/registered.html', locals())
                    # 当一切都OK的情况下，创建新用户
                    print(username, password1, phone)
                    new_user = UserInfo.objects.create()
                    new_user.username = username
                    new_user.password = password1
                    # new_user.email = email
                    # new_user.gender = sex
                    new_user.phone = phone
                    new_user.up_time = datetime.datetime.now()
                    new_user.save()
                    return redirect('login')  # 自动跳转到登录页面
    register_form = RegisterForm()
    return render(request, 'user_app/registered.html', locals())


def logout(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("index")
    request.session.flush()
    # 或者使用下面的方法
    # del request.session['is_login']
    # del request.session['user_id']
    # del request.session['user_name']
    return redirect("index")


def user(request):
    '''
    访问我的订单
    :param request:
    :return:
    '''
    return render(request, 'user_app/user.html')


def user_info(request):
    '''
    访问个人信息
    :param request:
    :return:
    '''
    return render(request, 'user_app/user_info.html')


def user_password(request):
    '''
    访问修改密码
    :param request:
    :return:
    '''
    return render(request, 'user_app/user_Password.html')


def user_collect(request):
    '''
    访问我的收藏
    :param request:
    :return:
    '''
    return render(request, 'user_app/user_Collect.html')


def user_address(request):
    '''
    访问收货地址管理
    :param request:
    :return:
    '''
    return render(request, 'user_app/user_address.html')
