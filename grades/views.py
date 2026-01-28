# 导入ListView 等
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from django.urls import reverse_lazy

from utils.premissions import RoleRequiredMixin
# 导入ListView使用时所需要提供的模型
from .models import Grade
from .forms import GradeForm

# Create your views here.
class GradeBaseView(RoleRequiredMixin):
    """
    定义一个基类，继承自 object
    """
    # 模型
    model = Grade
    # 模板
    template_name = 'grades/form.html'
    # 表单
    form_class = GradeForm
    # 重定向
    success_url = reverse_lazy('grade_list')
    # 返回的数据
    context_object_name = 'grades'
    allowed_roles = ['admin',]

class GradeListView(GradeBaseView, ListView):
    # 指定模板
    template_name = 'grades/list.html'
    # 显示字段
    fields = ['grade_name', 'grade_number']
    # 定义每页显示的数据条数
    paginate_by = 10

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

class GradeCreateView(GradeBaseView, CreateView):
    pass

class GradeUpdateView(GradeBaseView, UpdateView):
    pass

class GradeDeleteView(GradeBaseView, DeleteView):
    template_name = 'grades/delete_confirm.html'