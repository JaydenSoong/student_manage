from django.views.generic import ListView, UpdateView, CreateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.db.models import Q

from .models import Score
from .forms import ScoreForm
from grades.models import Grade
from students.models import Student


# Create your views here.
class ScoreBasicView:
    model = Score
    reverse_lazy('score-list')

class ScoreListView(ScoreBasicView, ListView):
    template_name = 'scores/list.html'
    paginate_by = 9
    context_object_name = 'scores'

    # 重写get_queryset 方法，添加搜索功能
    def get_queryset(self):
        # 使用父类的方法，获取所有学生
        queryset = super().get_queryset()
        grade_id = self.request.GET.get('grade')
        keywords = self.request.GET.get('search')

        if grade_id:
            queryset = queryset.filter(grade__pk=grade_id)
        if keywords:
            queryset = queryset.filter(
                Q(student_number=keywords) |
                Q(student_name=keywords)
            )
        return queryset
    # 默认的 context 返回的 student 对象，由于我们还要在页面中使用 grade 对象，所以可以重写 get_context_data 方法
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 获取所有班级并添加到上下文对象
        context['grades'] = Grade.objects.all().order_by('grade_number')
        # 判断当前选中的班级，并添加到上下文对象中
        context['current_grade'] = self.request.GET.get('grade', '')
        return context

class ScoreUpdateView(UpdateView):
    model = Score
    template_name = 'scores/score_update.html'
    fields = ['score_name', 'score_value', 'score_type']
    success_url = reverse_lazy('scores:score_list')

class ScoreCreateView(CreateView):
    template_name = 'scores/form.html'
    form_class = ScoreForm

    # 表单验证成功后的处理逻辑
    def form_valid(self, form):
        self.object = form.save()
        return JsonResponse({
            'status': 'success',
            'message': '添加成功'
        }, status=200)

    # 表单验证失败后的处理逻辑
    def form_invalid(self, form):
        # 获取表单返回的错误信息
        errors = form.errors.as_json()
        return JsonResponse({
            'status': 'error',
            'message': errors
        }, status=400)


class ScoreDeleteView(DeleteView):
    model = Score
    template_name = 'scores/score_delete.html'
    success_url = reverse_lazy('scores:score_list')

class ScoreDeleteMultipleView(DeleteView):
    model = Score
    template_name = 'scores/score_delete_multiple.html'
    success_url = reverse_lazy('scores:score_list')

class ScoreDetailView(ListView):
    model = Score
    template_name = 'scores/score_detail.html'
    context_object_name = 'score_detail'
    ordering = ['-id']

    def get_queryset(self):
        return Score.objects.filter(student_id=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = '成绩详情'
        return context

def score_export(request):
    pass

def score_import(request):
    pass

class MyScoreListView(ListView):
    model = Score
    template_name = 'scores/my_score_list.html'