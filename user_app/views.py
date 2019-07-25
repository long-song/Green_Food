from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
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

import random
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest

'''发送短信(手机,6位验证码)'''
def send_sms(phone, code):
    client = AcsClient('LTAIEx3Gbdbceg2C', 'MsCoWUm3x2iXaIcvtqhQLi9yj6nHxX', 'cn-hangzhou')

    code = "{'code':%s}" % (code)
    request = CommonRequest()
    request.set_accept_format('json')
    request.set_domain('dysmsapi.aliyuncs.com')
    request.set_method('POST')
    request.set_protocol_type('https')  # https | http
    request.set_version('2017-05-25')
    request.set_action_name('SendSms')

    request.add_query_param('RegionId', 'cn-hangzhou')
    request.add_query_param('PhoneNumbers', phone)
    request.add_query_param('SignName', '北网实训组')
    request.add_query_param('TemplateCode', 'SMS_165745016')
    request.add_query_param('TemplateParam', code)

    response = client.do_action(request) # 开始向手机发送验证码
    # python2:  print(response)
    print(str(response, encoding='utf-8'))

    return str(response, encoding='utf-8')

# 生成验证码函数
def get_code(n=6, alpha=True):
    """
    生成随机验证码
    :param n: 代表生成几位验证码
    :param alpha: True表示生成带有字母的  False不带字母的
    :return:
    """
    s = ''  # 创建字符串变量,存储生成的验证码
    for i in range(n):  # 通过for循环控制验证码位数
        num = random.randint(0, 9)  # 生成随机数字0-9
        if alpha:  # 需要字母验证码,不用传参,如果不需要字母的,关键字alpha=False
            upper_alpha = chr(random.randint(65, 90)) # chr()：将数字转换成对应的ASCII值
            lower_alpha = chr(random.randint(97, 122))
            num = random.choice([num, upper_alpha, lower_alpha])
        s = s + str(num)
    return s

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

# 登录函数
def login(request):
    '''
        访问登录页面
        :param request:
        :return:
        '''
    if request.method == "GET":
        code = get_code(6 , False)
        send_sms('15103455631', code)
        print(code)
        request.session['code'] = code
        return render(request, 'user_app/Login.html')
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        var_code = request.POST.get('var_code')
        code = request.session['code']
        print(username,password,var_code)
        if var_code == code:
            try:
                user = UserInfo.objects.get(username=username)
                if user.password == password:
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_username'] = user.username
                    # request.session['user_head'] = user.head_img
                    return redirect('index')
                else:
                    message = "密码不正确！"
            except:
                message = "用户不存在！"
        else:
            message = "验证码不正确！"
        return render(request, 'user_app/Login.html', locals())
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
@login_required
def user(request):
    '''
    访问我的订单
    :param request:
    :return:
    '''
    return render(request, 'user_app/user.html')

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
    return render(request, 'user_app/user_info.html',{'user':user})

# 修改密码函数
@login_required
def user_password(request):
    '''
    访问修改密码
    :param request:
    :return:
    '''
    return render(request, 'user_app/user_Password.html')

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
    return render(request, 'user_app/user_address.html')

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
        print(new_gender,new_username,new_birthday,new_email,new_phone,new_t_name)
        a = request.session['user_id']
        user = UserInfo.objects.get(id=a)
        user.username = new_username
        user.t_name = new_t_name
        user.phone = new_phone
        user.gender = new_gender
        user.birthday = new_birthday
        user.email = new_email
        user.save()
        return render(request, 'user_app/user_info.html',{'user':user})
    return render(request, 'user_app/user_info_set.html')
