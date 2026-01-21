from django.db import models
from django.contrib.auth.models import User
from grades.models import Grade

GENDER_CHOICES = (
    ('M', '男'),
    ('F', '女'),
)
# Create your models here.
class Student(models.Model):
    student_number = models.CharField(max_length=20, unique=True, null=True, verbose_name='学号')
    student_name = models.CharField(max_length=20, verbose_name='姓名')
    gender = models.CharField(max_length=1, verbose_name='性别', choices=GENDER_CHOICES)
    birthday = models.DateField(verbose_name='出生日期', help_text='格式：2023-01-01')
    contact_number = models.CharField(max_length=11, verbose_name='联系方式')
    address = models.CharField(max_length=50, verbose_name='地址')

    # 和 Django 的 User 模型一对一关联
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='用户')

    # 与班级模型一对多关联
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, verbose_name='班级', related_name='students')

    def __str__(self):
        return self.user.username

    class Meta:
        db_table = 'student'
        verbose_name = '学生信息'
        verbose_name_plural = verbose_name