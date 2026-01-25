from django import forms
from django.core.exceptions import ValidationError
import datetime

from grades.models import Grade
from .models import Teacher

GENDER_CHOICES = (
    ('M', '男'),
    ('F', '女'),
)

class TeacherForm(forms.ModelForm):
    # 重写父类方法，对象属性grade进行排序
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['grade'].queryset = Grade.objects.all().order_by('grade_number')
        self.fields['grade'].empty_label = '请选择班级'
        self.fields['gender'].widget = forms.Select(choices=GENDER_CHOICES)

    # 验证老师所管理的班级（这里设定的是班主任，所以与班级的关系是一对一的）
    def clean_grade(self):
        grade = self.cleaned_data['grade']
        if Teacher.objects.filter(grade=grade).exclude(pk=self.instance.pk).exists():
            raise ValidationError('具有管理该班级的老师信息已经存在')
        return grade


    # 验证出生日期
    def clean_birthday(self):
        birthday = self.cleaned_data['birthday']
        # 验证生日格式
        if not isinstance(birthday, datetime.date):
            raise ValidationError('生日格式错误，正确格式为：2023-01-01')
        if birthday > datetime.date.today():
            raise ValidationError('生日不能大于当前日期')
        return birthday

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        # 验证联系方式格式
        if Teacher.objects.filter(phone_number=phone_number).exclude(pk=self.instance.pk).exists():
            raise ValidationError('具有该手机号的老师信息已经存在')
        return phone_number

    class Meta:
        model = Teacher
        fields = ['teacher_name', 'grade', 'phone_number', 'gender', 'birthday']