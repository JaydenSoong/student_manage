# 导入ListView
from django.views.generic import ListView
# 导入ListView使用时所需要提供的模型
from .models import Grade

# Create your views here.
class GradeListView(ListView):
    # 指定模型
    model = Grade
    # 指定模板
    template_name = 'grades/list.html'
    # 显示字段
    fields = ['grade_name', 'grade_number']
    # 返回的数据
    context_object_name = 'grades'
