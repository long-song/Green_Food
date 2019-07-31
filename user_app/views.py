from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from user_app.models import *
from django.db.models import F,Q
from user_app.models import UserInfo
from user_app.froms import UserForm, RegisterForm
import datetime
from django.conf import settings

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

# 登录验证函数
def login_required(view_func):
    """
    登录装饰器函数
    :return:
    """

    # print('login_required=',view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.has_key('is_login'):
            return redirect('login')

        return view_func(request, *args, **kwargs)

    return wrapper

from common.code import *
from common.phone_num4 import *
# 获取手机号发送验证码
# 在发送ajax的post请求时解决跨网站请求
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def phone_code(request):
    '''
    获取手机号发送验证码
    :param request:
    :return:
    '''
    if request.method == "POST":
        phone = request.POST.get('phone')
        phone_n = phone_num(phone)
        if phone_n != '请输入正确的手机号':
            code = get_code(6, False)
            print(code)
            send_sms(phone, code)
            request.session['code'] = code
            message = "OK"
            return JsonResponse({'message':message})
        else:
            print(1)
            message = "手机号不正确"
            return JsonResponse({'message':message})

# 登录函数
def login(request):
    '''
        访问登录页面
        :param request:
        :return:
        '''
    if request.session.has_key('is_login'):
        return redirect('user_info')
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        var_code = request.POST.get('var_code')
        code = request.session.get('code')
        try:
            user = UserInfo.objects.get(Q(username=username)|Q(phone=username))
            if user.password == password:
                if var_code == code:
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_username'] = user.username
                    # request.session['user_head'] = user.head_img
                    return redirect('index')
                else:
                    message = "验证码不正确！"
            else:
                message = "密码不正确！"
        except:
            # print(1)
            message = "用户不存在！"
        return render(request, 'user_app/Login.html',locals())
    else:
        return render(request, 'user_app/Login.html', locals())


# 注册函数
def registered(request):
    '''
    访问注册页面
    :param request:
    :return:
    '''
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
                    same_phone_user = UserInfo.objects.filter(phone=phone)
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


# 注销函数
@login_required
def logout(request):
    request.session.flush()
    # 或者使用下面的方法
    # del request.session['is_login']
    # del request.session['user_id']
    # del request.session['user_name']
    return redirect("index")


# 我的订单函数
# 导入生成唯一订单号函数
from common.orderNo import get_order_code
@login_required
def user(request):
    '''
    访问我的订单
    :param request:
    :return:
    '''
    a = request.session['user_id']
    user = UserInfo.objects.get(id=a)
    if request.method == 'GET':
        order_No = get_order_code()
        return render(request, 'user_app/user.html', locals())
    return render(request, 'user_app/user.html',locals())


# 个人信息函数
@login_required
def user_info(request):
    '''
    访问个人信息
    :param request:
    :return:
    '''
    a = request.session['user_id']
    user = UserInfo.objects.get(id=a)
    # print(user.head_img)
    return render(request, 'user_app/user_info.html', {'user': user})


# 修改密码函数
@login_required
def user_password(request):
    '''
    访问修改密码
    :param request:
    :return:
    '''
    a = request.session['user_id']
    user = UserInfo.objects.get(id=a)
    if request.method=="POST":
        old_pwd = request.POST.get('old_pwd')
        new_pwd = request.POST.get('new_pwd')
        new_pwd1 = request.POST.get('new_pwd1')
        if old_pwd==user.password:
            if new_pwd != old_pwd:
                if new_pwd == new_pwd1:
                    user.password = new_pwd
                    user.save()
                    request.session.flush()
                    message = '您已成功修改密码，请重新登录！'
                    return render(request,'user_app/Login.html',{'meaasge':message})
                else:
                    message = '两次新密码输入不一致！'
            else:
                message = '新密码不能与原密码相同'
        else:
            message = '原密码输入错误！'
        return render(request, 'user_app/user_Password.html', locals())
    return render(request, 'user_app/user_Password.html', {'user': user})


# 我的收藏函数
@login_required
def user_collect(request):
    '''
    访问我的收藏
    :param request:
    :return:
    '''
    return render(request, 'user_app/user_Collect.html')


# 我的地址管理函数
@login_required
def user_address(request):
    '''
    访问收货地址管理
    :param request:
    :return:

    '''
    if request.method == "GET":
        a = request.session['user_id']
        user = UserInfo.objects.get(id=a)
        # addre = Adress.objects.get(user_id=a)
        addres = Adress.objects.filter(user_id=a)
        # print(addre.postcode)
        return render(request, 'user_app/user_address.html', {'user': user,'addres':addres})

# 增加用户地址
def  user_address_add(request):
    """
    增加用户地址
    :param request:
    :return:
    """
    if request.method == "GET":
        a = request.session['user_id']
        user = UserInfo.objects.get(id=a)
        addre = Adress.objects.filter(user_id=a)
        # print(user.head_img)
        return render(request, 'user_app/user_address_add.html', {'user': user})
    if request.method == "POST":
        a = request.session['user_id']
        new_aname = request.POST.get('new_aname')
        new_area = request.POST.get('new_area')
        new_postcode = request.POST.get('new_postcode')
        new_aphone = request.POST.get('new_aphone')
        new_ads = request.POST.get('new_ads')
        addre1 = Adress(aname=new_aname,area=new_area,postcode=new_postcode,
                        aphone=new_aphone,ads=new_ads,user_id=a)
        addre1.save()
        print(new_aname, new_area, new_postcode, new_aphone, new_ads)


        return redirect('user_address')
    return render(request, 'user_app/user_address_add.html')


# 修改用户地址
def  user_address_change(request,id):
    """
    修改用户地址
    :param request:
    :return:
    """


    if request.method == "GET":
        a = request.session['user_id']
        user = UserInfo.objects.get(id=a)
        addre2 = Adress.objects.get(pk=id)
        # print(user.head_img)
        return render(request, 'user_app/user_address_change.html', {'addre2': addre2,"user":user})
    if request.method == "POST":
        a = request.session['user_id']
        new_aname = request.POST.get('new_aname')
        new_area = request.POST.get('new_area')
        new_postcode = request.POST.get('new_postcode')
        new_aphone = request.POST.get('new_aphone')
        new_ads = request.POST.get('new_ads')
        addre2 = Adress.objects.get(id=id)
        addre2.aname = new_aname
        addre2.area = new_area
        addre2.postcode = new_postcode
        addre2.aphone = new_aphone
        addre2.ads = new_ads
        addre2.user_id = a
        addre2.save()
        user = UserInfo.objects.get(id=a)
        addres = Adress.objects.filter(user_id=a)
        print(new_aname, new_area, new_postcode, new_aphone, new_ads)

        return render(request, 'user_app/user_address.html', {'user': user, 'addres': addres,'id':addre2.id})

# 删除用户地址
def  user_address_delete(request,id):
    """
    删除用户地址
    :param request:
    :return:
    """
    addre3 = Adress.objects.get(pk=id)
    addre3.delete()


    return redirect('user_address')


# 个人资料修改函数
@login_required
def user_info_set(request):
    '''
    访问个人资料修改页面
    :param request:
    :return:
    '''
    if request.method == "GET":
        a = request.session['user_id']
        user = UserInfo.objects.get(id=a)
        # print(user.head_img)
        return render(request, 'user_app/user_info_set.html', {'user': user})
    if request.method == "POST":
        new_username = request.POST.get('new_name')
        new_t_name = request.POST.get('new_t_name')
        new_gender = request.POST.get('1')
        new_email = request.POST.get('new_email')
        new_birthday = request.POST.get('new_birthday')
        new_phone = request.POST.get('new_phone')
        print(new_gender, new_username, new_birthday, new_email, new_phone, new_t_name)
        a = request.session['user_id']
        user = UserInfo.objects.get(id=a)
        user.username = new_username
        user.t_name = new_t_name
        user.phone = new_phone
        user.gender = new_gender
        user.birthday = new_birthday
        user.email = new_email
        user.save()
        return redirect('user_info')
    return render(request, 'user_app/user_info_set.html')

# 修改头像函数
@login_required
def new_head(request):
    '''
    访问个人资料修改页面
    :param request:
    :return:
    '''
    if request.method == "GET":
        a = request.session['user_id']
        user = UserInfo.objects.get(id=a)
        return render(request, 'user_app/new_head.html', {'user': user})
    if request.method == "POST":
        new_head = request.FILES.get('new_head')
        a = request.session['user_id']
        user = UserInfo.objects.get(id=a)
        user.head_img = new_head
        user.save()
        return redirect('user_info')
    return render(request, 'user_app/new_head.html')