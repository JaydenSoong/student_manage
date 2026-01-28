from django import forms
from django.core.exceptions import ValidationError

ROLE_CHOICES = [
    ('student', '学生'),
    ('teacher', '老师'),
    ('admin', '管理员'),
]

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入用户名'}),
        required=True,
    )
    password = forms.CharField(
        max_length=20,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入密码'}),
        required=True,
    )

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        required=True,
        label='角色',
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) == 0:
            raise ValidationError('用户名长度不能为0')
        return username
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) == 0:
            raise ValidationError('密码长度不能为0')
        return password
