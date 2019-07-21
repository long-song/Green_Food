from django import forms
from captcha.fields import CaptchaField


class UserForm(forms.Form):
    username = forms.CharField(label="用户名", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="密码", max_length=256, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    captcha = CaptchaField(label='验证码')


class RegisterForm(forms.Form):
    gender = (
        ('male', "男"),
        ('female', "女"),
    )
    username = forms.CharField(label="用户名", max_length=128, required=True, error_messages={'required': '用户名不能为空.'},
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label="密码", max_length=256, min_length=6,
                                error_messages={'required': '密码不能为空.', 'min_length': "至少6位"},
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label="确认密码",max_length=256, min_length=6,
                                error_messages={'required': '密码不能为空.', 'min_length': "至少6位"},
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    phone = forms.IntegerField(label='手机号')
    # email = forms.EmailField(label="邮箱地址", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    # sex = forms.ChoiceField(label='性别', choices=gender)
    captcha = CaptchaField(label='验证码')
