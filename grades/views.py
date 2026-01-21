# 导入ListView
from django.views.generic import ListView
# 导入ListView使用时所需要提供的模型
from .models import Grade
from django.db.models import Q

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

    # 定义每页显示的数据条数
    paginate_by = 5

    # 重写父类方法
    def get_queryset(self):
        # 默认返回所有数据
        queryset = super().get_queryset()
        # 确定查询条件
        search = self.request.GET.get('search')

        if search:
            # 使用 contains 方法进行模糊匹配, icontains 表示忽略大小写, 并且使用 Q 对象进行组合
            queryset = queryset.filter(
                Q(grade_name__icontains=search) |
                Q(grade_number__icontains=search)
            )

        # 如果存在参数，则进行过滤，否则返回所有数据（父类方法）
        return queryset
