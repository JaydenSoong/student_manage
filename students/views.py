from django.http import JsonResponse
from django.views.generic import ListView, CreateView
from django.db.models import Q
from django.urls import reverse_lazy

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

    def form_valid(self, form):
        # # 获取用户输入的性别
        # sex = form.cleaned_data['sex']
        # # 获取用户输入的出生日期
        # birthday = form.cleaned_data['birthday']
        # # 获取用户输入的联系方式
        # contact_number = form.cleaned_data['contact_number']
        # # 获取用户输入的班级
        # grade = form.cleaned_data['grade']
        # # 获取用户输入的班级编号
        # grade_number = grade.grade_number
        # # 获取用户输入的班级名称


        return JsonResponse({
            'status': 'success',
            'message': '添加成功'
        })