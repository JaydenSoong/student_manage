from django import forms
from django.core.exceptions import ValidationError
import datetime
from .models import Student
from grades.models import Grade

class StudentForm(forms.ModelForm):
    # 重写父类方法，对象属性grade进行排序
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['grade'].queryset = Grade.objects.all().order_by('grade_number')

    # 验证学生姓名,方法名格式固定的，为 clean_+字段名
    def clean_student_name(self):
        student_name = self.cleaned_data['student_name']
        # 只是简单的验证一下长度
        if len(student_name) < 2 or len(student_name) > 20:
            raise ValidationError('请填写正确的学生姓名')
        return student_name

    # 验证学号,方法名格式固定的，为 clean_+字段名
    def clean_student_number(self):
        student_number = self.cleaned_data['student_number']
        # 同样的也是验证一下长度
        if len(student_number) != 8:
            raise ValidationError('学号长度必须为8位数字')
        return student_number

    # 验证出生日期
    def clean_birthday(self):
        birthday = self.cleaned_data['birthday']
        # 验证生日格式
        if not isinstance(birthday, datetime.date):
            raise ValidationError('生日格式错误，正确格式为：2023-01-01')
        if birthday > datetime.date.today():
            raise ValidationError('生日不能大于当前日期')
        return birthday

    def clean_contact_number(self):
        contact_number = self.cleaned_data['contact_number']
        # 验证联系方式格式
        if len(contact_number) != 11:
            raise ValidationError('手机号码长度必须为11位')
        return contact_number

    class Meta:
        model = Student
        fields = ['student_number', 'student_name', 'gender', 'grade', 'birthday', 'contact_number', 'address']