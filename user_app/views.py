from django.shortcuts import render, redirect, HttpResponse, reverse
from django.http import JsonResponse
from user_app.models import *
from django.db.models import F, Q
from user_app.models import UserInfo
from user_app.froms import UserForm, RegisterForm
import datetime
from integral_app.models import *
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
    return render(request, 'index.html', {'index': 'index'})


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
    return render(request, 'user_app/user_Password.html', {'user': user})


# 我的收藏函数
@login_required
def user_collect(request):
    '''
    访问我的收藏
    :param request:
    :return:
    '''
    a = request.session['user_id']
    user = UserInfo.objects.get(id=a)
    pro_id = request.GET.get("id")
    fav = request.GET.get("fav")
    if pro_id != None:
        if fav == "1":
            pro = Pro_sku.objects.get(id=pro_id)
            collect = Collect.objects.create()
            collect.pro_id = pro_id
            collect.image = pro.image
            collect.name = pro.name
            collect.size = pro.size
            collect.title = pro.title
            collect.price = pro.price
            collect.user_id = a
            collect.save()
            collect1 = Collect.objects.filter(user=a)
            return render(request, 'user_app/user_Collect.html', {'user': user, 'col': collect1, 'fav': fav})
        else:
            collect = Collect.objects.filter(user=a, pro_id=pro_id)
            collect.delete()
            collect1 = Collect.objects.filter(user=a)
            return render(request, 'user_app/user_Collect.html', {'user': user, 'col': collect1, 'fav': fav})
    else:
        collect1 = Collect.objects.filter(user_id=a)
        return render(request, 'user_app/user_Collect.html', {'user': user, 'col': collect1})


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
        return render(request, 'user_app/user_address.html', {'user': user, 'addres': addres})


# 设置默认地址
def user_address_default(request, id):
    '''
    设置默认地址
    :param request:
    :return:
    '''
    user = request.session['user_id']
    adress = Adress.objects.get(user=user, is_default=True)
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
        return render(request, 'user_app/user_address_add.html', {'user': user})
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
            return render(request, 'user_app/user_address_add.html',{'user':user1,'res': 0, 'errmsg': '信息输入不完整'})
        phone_n = phone_num(new_aphone)
        if phone_n == '请输入正确的手机号':
            return render(request, 'user_app/user_address_add.html', {'user':user1,'res': 1, 'errmsg': '手机号输入不正确'})

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
        return render(request, 'user_app/user_address_change.html', {'addre2': addre2, "user": user})
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
