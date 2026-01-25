from django.db import models

from grades.models import Grade

# Create your models here.
class Score(models.Model):
    """
    成绩表
    """
    title = models.CharField('考试名称', max_length=20, help_text="title/考试名称")
    student_number = models.CharField('学号', max_length=20, help_text="student_number/学号")
    student_name = models.CharField('姓名', max_length=20, help_text="student_name/姓名")
    chinese_score = models.DecimalField('语文成绩', max_digits=5, decimal_places=2, help_text="chinese_score/语文成绩")
    math_score = models.DecimalField('数学成绩', max_digits=5, decimal_places=2, help_text="math_score/数学成绩")
    english_score = models.DecimalField('英语成绩', max_digits=5, decimal_places=2, help_text="english_score/英语成绩")
    # 与班级表一对多关联
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, verbose_name='班级', related_name='score')

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'score'
        verbose_name = '成绩信息'
        verbose_name_plural = verbose_name