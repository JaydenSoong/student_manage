from django.db import models
from django.contrib.auth.models import User

from grades.models import Grade

GENDER_CHOICES = (
    ('M', '男'),
    ('F', '女'),
)

# Create your models here.
class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher')
    teacher_name = models.CharField('老师姓名', max_length=20)
    phone_number = models.CharField('手机号码', max_length=11, unique= True)
    gender = models.CharField('性别', max_length=1, choices=GENDER_CHOICES)
    birthday = models.DateField('出生日期', help_text='格式为：2020-01-01')
    grade = models.OneToOneField(Grade, on_delete=models.DO_NOTHING, related_name='teacher', verbose_name='负责班级')

    def __str__(self):
        return self.teacher_name

    class Meta:
        db_table = 'teacher'
        verbose_name = '教师信息'
        verbose_name_plural = verbose_name