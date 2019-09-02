from django.core.mail import send_mail
from django.conf import settings
from celery import Celery
import time

# 创建一个Celery类的实例,第一个参数内容任意，一般都传当前路径
app = Celery("celery_tasks.tasks",broker="redis://localhost:6379/8")

# 定义任务函数
@app.task
def send_register_active_mail(to_email,user_name,token):
    """
    发送激活邮件
    :param to_email: 收件人地址
    :param user_name: 发送邮件的用户名
    :param token: 用户加密信息的密文
    :return:
    """
    subject = "浦江县食品商城欢迎信息"  # 邮件标题
    message = "普通字符串"  # 邮件正文
    sender = settings.EMAIL_FROM  # 发件人
    receiver = [to_email]  # 收件人列表
    html_message = "<h1>%s,欢迎您成为浦江食品商城会员</h1>请点击下面的链接激活您的账户<br/><a href='http://127.0.0.1:8000/user_app/active/%s'>http://127.0.0.1:8000/user_app/active/%s</a>" % (
        user_name, token, token)  # 邮件正文
    # 只有使用html_message传递的html字符串才会被正常解析
    send_mail(subject, message, sender, receiver, html_message=html_message)

    time.sleep(5)  # 休眠5秒，模拟发送邮件需要耗时5秒的情况

