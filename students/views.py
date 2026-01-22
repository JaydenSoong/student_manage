from django.http import JsonResponse
from django.views.generic import ListView, CreateView
from django.db.models import Q
from django.urls import reverse_lazy
from django.contrib.auth.models import User

from .models import Student
from .forms import StudentForm

# Create your views here.
class StudentListView(ListView):
    model = Student
    template_name = 'students/list.html'
    context_object_name = 'students'

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(sex__icontains=search) |
                Q(birthday__icontains=search)
            )
        return queryset

class StudentCreateView(CreateView):
    model = Student
    template_name = 'students/form.html'
    form_class = StudentForm
    success_url = reverse_lazy('student_list')

    # 表单验证成功后的处理逻辑
    def form_valid(self, form):
        # student 表和 user 表是一对一关联，所以接收学号字段，来作为 user 的 username
        student_number = form.cleaned_data['student_number']

        # 检查是user表中否已存在该用户
        users = User.objects.filter(username=student_number)
        if users.exists():
            user = users.first()
        else:
            # 如果不存在该用户，则创建该用户
            user = User.objects.create_user(username=student_number, password=student_number[-6:])
        # 写入到student表中
        form.instance.user = user
        form.save()

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