from django import forms
from django.core.exceptions import ValidationError
import datetime

from students.models import Student
from .models import Score
from grades.models import Grade

class ScoreForm(forms.ModelForm):
    # 重写父类方法，对象属性grade进行排序
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['grade'].queryset = Grade.objects.all().order_by('grade_number')
        self.fields['grade'].empty_label = '请选择班级'

    # 验证学生姓名,方法名格式固定的，为 clean_+字段名
    def clean_student_name(self):
        student_name = self.cleaned_data['student_name']
        # 只是简单的验证一下长度
        if len(student_name) < 2 or len(student_name) > 20:
            raise ValidationError('请填写正确的学生姓名')
        if not Student.objects.filter(student_name=student_name).exists():
            raise ValidationError('该学生姓名不存在')
        return student_name

    # 验证学号,方法名格式固定的，为 clean_+字段名
    def clean_student_number(self):
        student_number = self.cleaned_data['student_number']
        # 同样的也是验证一下长度
        if len(student_number) != 8:
            raise ValidationError('学号长度必须为8位数字')
        if not Student.objects.filter(student_number=student_number).exists():
            raise ValidationError('该学号不存在')
        return student_number

    # 验证学生学号班级是否能匹配
    def clean(self):
        cleaned_data = super().clean()
        student_name = cleaned_data.get('student_name')
        student_number = cleaned_data.get('student_number')
        grade = cleaned_data.get('grade')
        if student_name and student_number and grade:
            try:
                student = Student.objects.get(student_name=student_name, student_number=student_number, grade=grade)
                cleaned_data['student'] = student
            except Student.DoesNotExist:
                raise ValidationError('该学生信息不存在')
        return cleaned_data


    class Meta:
        model = Score
        fields = ['title', 'student_name', 'student_number', 'grade', 'chinese_score', 'math_score', 'english_score']
