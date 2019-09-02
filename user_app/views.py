from django.shortcuts import render, redirect, HttpResponse, reverse
from django.http import JsonResponse
from django.db.models import F, Q
from integral_app.models import *
import datetime
import time
from user_app.models import *
from django.core.mail import send_mail
from celery_tasks.tasks import send_register_active_mail
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired
from django.contrib.auth.hashers import check_password
from django.conf import settings


# Create your views here.
def index(request):
    '''
    访问首页
    :param request:
    :return:
    '''
    skus = Pro_sku.objects.filter(is_index=True)
    # print(skus)
    return render(request, 'index.html', {'index': 'index','skus':skus})


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
            return JsonResponse({'message': message})
        else:
            print(1)
            message = "手机号不正确"
            return JsonResponse({'message': message})


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
            user = UserInfo.objects.get(Q(username=username) | Q(phone=username))
            if user.is_active:
                if user.password == password:
                    if var_code == code:
                        request.session['is_login'] = True
                        request.session['user_id'] = user.id
                        request.session['user_username'] = user.username
                        return redirect('index')
                    else:
                        message = "验证码不正确！"
                else:
                    message = "密码不正确！"
            else:
                message = "用户未激活！"
        except:
            # print(1)
            message = "用户不存在！"
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
    if request.method == "GET":
        # register_form = RegisterForm()
        return render(request, 'user_app/registered.html')
    if request.method == "POST":
        queryDict = request.POST
        user_name = queryDict.get('username')
        password1 = queryDict.get('password1')
        password2 = queryDict.get('password2')
        phone = queryDict.get('phone')
        email = queryDict.get('email')
        confirm = queryDict.get('confirm')
        print(locals())
        # sex = register_form.cleaned_data['sex']
        # 2.校验数据的准确性
        # A: 校验数据是否输入内容:all([]):如果列表中所有的内容都不为空则返回True,否则返回False
        if not all([user_name, password1, password2, phone, email, confirm]):
            return render(request, 'user_app/registered.html', {'errmsg': '请务必输入完整信息哦！'})

        if password1 != password2:
            return render(request, 'user_app/registered.html', {'errmsg': '密码输入不一致！'})

        if not re.match('[a-z0-9][\w\.-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}', email):
            return render(request, 'user_app/registered.html', {'errmsg': '邮箱格式非法！'})

        if confirm != 'on':
            return render(request, 'user_app/registered.html', {'errmsg': '请同意协议！'})

        # 判断手机号是否合法
        phone_n = phone_num(phone)
        if phone_n == '请输入正确的手机号':
            return render(request, 'user_app/registered.html', {'errmsg': '请输入正确手机号！'})
        phone0 = None
        try:
            phone0 = UserInfo.objects.get(phone=phone)
        except UserInfo.DoesNotExist:
            phone0 = None

        if phone0:
            return render(request, 'user_app/registered.html', {'errmsg': '该手机号已被注册！'})
        # 判断注册的用户是否存在
        user = None
        try:
            # 说明用户已经存在,不能注册
            user = UserInfo.objects.get(username=user_name)
        except UserInfo.DoesNotExist:
            # 说明用户不存在，可以注册
            user = None

        if user:  # 说明用户已经存在
            return render(request, 'user_app/registered.html', {'errmsg': '用户%s已经存在，请更换用户后再注册' % user_name})

        # 3.完成注册的核心业务功能
        # 新办法
        user = UserInfo.objects.create(username=user_name, password=password1, email=email, phone=phone,
                                            up_time=datetime.datetime.now())
        user.is_active = 0
        user.save()
        print('user=', user)

        # 实现对指定数据的加密
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {'confirm': user.id}
        token = serializer.dumps(info)
        token = token.decode()  # 默认是utf-8对字节进行解码
        print('token=', token)

        # 发送邮件，让用户激活自己的账号
        # 发送的激活链接如：http://127.0.0.1:8000/active/用户id
        # subject = "浦江县食品商城欢迎信息"  # 邮件标题
        # message = "普通字符串"  # 邮件正文
        # sender = settings.EMAIL_FROM  # 发件人
        # receiver = [email]  # 收件人列表
        # html_message = "<h1>%s,欢迎您成为浦江食品商城会员</h1>请点击下面的链接激活您的账户<br/><a href='http://127.0.0.1:8000/user_app/active/%s'>http://127.0.0.1:8000/user_app/active/%s</a>" % (
        #     user_name, token, token)  # 邮件正文
        # # 只有使用html_message传递的html字符串才会被正常解析
        # send_mail(subject, message, sender, receiver, html_message=html_message)
        send_register_active_mail.delay(email, user_name, token)
        time.sleep(5)
        return redirect('index')  # 自动跳转到首页


def active(request, token):
    """
    激活视图
    """

    if request.method == 'GET':
        try:
            # 实例化解密对象
            serializer = Serializer(settings.SECRET_KEY, 3600)

            # {'confirm':7}
            info = serializer.loads(token)
            user_id = info['confirm']
            # 根据用户id获取用户对象
            user = UserInfo.objects.get(id=user_id)
            user.is_active = 1
            user.save()
            return redirect(reverse('login'))
        except SignatureExpired:
            # 链接过期提示
            return HttpResponse('链接已过期')


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
    order = 'order'
    if request.method == 'GET':
        order_No = get_order_code()
        return render(request, 'user_app/user.html', locals())
    return render(request, 'user_app/user.html', locals())


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
    return render(request, 'user_app/user_info.html', {'user_info': 'user_info', 'user': user})


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
    if request.method == "GET":
        return render(request, 'user_app/user_Password.html', {'user_password':'user_password','user': user})
    if request.method == "POST":
        old_pwd = request.POST.get('old_pwd')
        new_pwd = request.POST.get('new_pwd')
        new_pwd1 = request.POST.get('new_pwd1')
        if old_pwd == user.password:
            if new_pwd != old_pwd:
                if new_pwd == new_pwd1:
                    user.password = new_pwd
                    user.save()
                    request.session.flush()
                    message = '您已成功修改密码，请重新登录！'
                    return render(request, 'user_app/Login.html', {'meaasge': message})
                else:
                    message = '两次新密码输入不一致！'
            else:
                message = '新密码不能与原密码相同'
        else:
            message = '原密码输入错误！'
        return render(request, 'user_app/user_Password.html', locals())



# 我的收藏函数
@login_required
def user_collect(request):
    '''
    访问我的收藏
    :param request:
    :return:
    '''
    if request.method == 'GET':
        a = request.session['user_id']
        user = UserInfo.objects.get(id=a)
        collect = Collect.objects.filter(user=a)
        print('user', user, 'collect', collect)
        return render(request, 'user_app/user_Collect.html', {'user': user, 'collect': collect})
    if request.method == 'POST':
        if request.session.has_key('is_login'):
            a = request.session['user_id']
        else:
            return JsonResponse({'message': '请先登录哦！'})
        pro_id = request.POST.get("id")
        fav = request.POST.get("fav")
        pro_id = Pro_sku.objects.get(id=int(pro_id))
        print('pro_id', pro_id, type(pro_id), 'fav', fav)
        if pro_id != None:
            if fav == "0":
                # pro = Pro_sku.objects.get(id=pro_id)
                collect = Collect.objects.create()
                collect.pro_sku = pro_id
                collect.user_id = a
                collect.save()
                return JsonResponse({'message': '收藏成功'})
            else:
                collect = Collect.objects.filter(user=a, pro_sku=pro_id)
                collect.delete()
                return JsonResponse({'message': '取消收藏'})
        else:
            return JsonResponse({'message': '没有产品可以收藏'})


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
        # addres = Adress.objects.get(user_id=a)
        addres = Adress.objects.filter(user_id=a)
        # print(addre.postcode)
        return render(request, 'user_app/user_address.html', {'user_address':'user_address','user': user, 'addres': addres})


# 设置默认地址
def user_address_default(request, id):
    '''
    设置默认地址
    :param request:
    :return:
    '''
    user = request.session['user_id']
    adress = None
    try:
        adress = Adress.objects.get(user=user, is_default=True)
    except:
        adress = None
    if adress:
        adress.is_default = False
        adress.save()
    adress_default = Adress.objects.get(id=id)
    adress_default.is_default = True
    adress_default.save()
    return redirect(reverse('user_address'))


# 增加用户地址
def user_address_add(request):
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
        return render(request, 'user_app/user_address_add.html', {'user_address':'user_address','user': user})
    if request.method == "POST":
        # 1.接收客户端发送过来的数据
        user = request.session['user_id']
        user1 = UserInfo.objects.get(id=user)
        queryDict = request.POST
        new_aname = queryDict.get('new_aname')
        province = queryDict.get('province')
        city = queryDict.get('city')
        county = queryDict.get('county')
        new_aphone = queryDict.get('new_aphone')
        new_ads = queryDict.get('new_ads')

        # 2.检验数据
        if not all([new_aname, province, city, county, new_aphone, new_ads]):
            return render(request, 'user_app/user_address_add.html', {'user': user1, 'res': 0, 'errmsg': '信息输入不完整'})
        phone_n = phone_num(new_aphone)
        if phone_n == '请输入正确的手机号':
            return render(request, 'user_app/user_address_add.html', {'user': user1, 'res': 1, 'errmsg': '手机号输入不正确'})

        # 2.1 对数据进行整理
        province = Province.objects.get(province_id=province)
        city = City.objects.get(city_id=city)
        county = County.objects.get(county_id=county)
        new_area = province.province_name + ' ' + city.city_name
        new_postcode = str(county.county_id)[0:6]
        # new_ads = county.county_name + ' ' + new_ads

        # 3.完成具体的业务逻辑：地址的添加
        # 如果用户已经存在默认的收货地址，添加的地址不作为默认的收货地址，否则作为默认的收货地址
        # 判断用户的默认收货地址是否存在
        try:
            # adress = Adress.objects.get(user=user,is_default=True)
            adress = Adress.objects.get(user=user, is_default=True)
        except Adress.DoesNotExist:
            adress = None

        if adress:
            # 存在默认收货地址
            is_default = False
        else:
            # 不存在默认收货地址
            is_default = True

        # 3.1添加收货地址
        address = Adress.objects.create(aname=new_aname, area=new_area, postcode=new_postcode,
                                        aphone=new_aphone, ads=new_ads, user_id=user,
                                        province_name=province, city_name=city, county_name=county,
                                        is_default=is_default)
        # 4.返回应答
        return redirect('user_address')


# 修改用户地址
def user_address_change(request, id):
    """
    修改用户地址
    :param request:
    :return:
    """
    if request.method == "GET":
        a = request.session['user_id']
        user = UserInfo.objects.get(id=a)
        addre2 = Adress.objects.get(id=id)
        return render(request, 'user_app/user_address_change.html', {'user_address':'user_address','addre2': addre2, "user": user})
    if request.method == "POST":
        # 1.接收客户端发送过来的数据
        user = request.session['user_id']
        user1 = UserInfo.objects.get(id=user)
        queryDict = request.POST
        new_aname = queryDict.get('new_aname')
        province = queryDict.get('province')
        city = queryDict.get('city')
        county = queryDict.get('county')
        new_aphone = queryDict.get('new_aphone')
        new_ads = queryDict.get('new_ads')

        # 2.检验数据
        if not all([new_aname, province, city, county, new_aphone, new_ads]):
            return render(request, 'user_app/user_address_add.html', {'user': user1, 'res': 0, 'errmsg': '信息输入不完整'})
        phone_n = phone_num(new_aphone)
        if phone_n == '请输入正确的手机号':
            return render(request, 'user_app/user_address_add.html', {'user': user1, 'res': 1, 'errmsg': '手机号输入不正确'})

        # 2.1 对数据进行整理
        province1 = Province.objects.get(province_id=province)
        city1 = City.objects.get(city_id=city)
        county1 = County.objects.get(county_id=county)
        new_area = province1.province_name + ' ' + city1.city_name
        new_postcode = str(county1.county_id)[0:6]
        # new_ads = county.county_name + ' ' + new_ads
        # 3.完成具体的业务逻辑：地址的添加

        # 修改收货地址
        print(id, type(id))
        addre2 = Adress.objects.get(id=id)
        addre2.aname = new_aname
        addre2.area = new_area
        addre2.postcode = new_postcode
        addre2.aphone = new_aphone
        addre2.ads = new_ads
        addre2.province_name_id = province1.id
        addre2.city_name_id = city1.id
        addre2.county_name_id = county1.id
        addre2.save()
        # 4.返回应答
        return redirect('user_address')


# 删除用户地址
def user_address_delete(request, id):
    """
    删除用户地址
    :param request:
    :return:
    """
    addre3 = Adress.objects.get(pk=id)
    addre3.delete()
    return redirect('user_address')


# 省份管理器
def province(request):
    '''
    获取省联动信息
    :param request:
    :param p_id:
    :return:
    '''
    if request.is_ajax():
        infos_list = []
        infos = Province.objects.all()
        for info in infos:
            infos_list.append({'parentid': info.province_id, 'cityname': info.province_name})
        return JsonResponse({'infos': infos_list})


# 城市管理器
def city(request):
    '''
    获取市联动信息
    :param request:
    :param p_id:
    :return:
    '''
    if request.is_ajax():
        p_id = request.POST.get('p_id')
        print('p_id=' + p_id)
        infos_list = []
        infos = City.objects.filter(province_id=p_id)
        for info in infos:
            infos_list.append({'parentid': info.city_id, 'cityname': info.city_name})
        return JsonResponse({'infos': infos_list, })


# 区县管理器
def county(request):
    '''
    获取区县联动信息
    :param request:
    :param p_id:
    :return:
    '''
    if request.is_ajax():
        p_id = request.POST.get('p_id')
        infos_list = []
        infos = County.objects.filter(city_id=p_id)
        for info in infos:
            infos_list.append({'parentid': info.county_id, 'cityname': info.county_name})
        return JsonResponse({'infos': infos_list})


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
        return render(request, 'user_app/user_info_set.html', {'user_info':'user_info','user': user})
    if request.method == "POST":
        # 1.接收客户端发送的信息
        a = request.session['user_id']
        user = UserInfo.objects.get(id=a)
        new_username = request.POST.get('new_name')
        new_t_name = request.POST.get('new_t_name')
        new_gender = request.POST.get('1')
        new_email = request.POST.get('new_email')
        new_birthday = request.POST.get('new_birthday')
        new_phone = request.POST.get('new_phone')

        # 2.检验数据
        if not all([new_username, new_t_name, new_gender, new_email, new_birthday, new_phone]):
            return render(request, 'user_app/user_info_set.html', {'user': user, 'res': 0, 'errmsg': '请务必填写正确信息！'})
        phone_n = phone_num(new_phone)
        if phone_n == '请输入正确的手机号':
            return render(request, 'user_app/user_info_set.html', {'user': user, 'res': 1, 'errmsg': '手机号输入不正确'})

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
    访问修改头像页面
    :param request:
    :return:
    '''
    if request.method == "GET":
        a = request.session['user_id']
        user = UserInfo.objects.get(id=a)
        return render(request, 'user_app/new_head.html', {'user_info':'user_info','user': user})
    if request.method == "POST":
        new_head = request.FILES.get('new_head')
        a = request.session['user_id']
        user = UserInfo.objects.get(id=a)
        user.head_img = new_head
        user.save()
        return redirect('user_info')
    return render(request, 'user_app/new_head.html')
