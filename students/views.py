from django.http import JsonResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

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

class StudentUpdateView(UpdateView):
    model = Student
    template_name = 'students/form.html'
    form_class = StudentForm
    # success_url = reverse_lazy('student_list')

    # 表单验证成功后的处理逻辑
    def form_valid(self, form):
        # 从表单中获取学生对象实例
        student = form.save(commit=False)
        # 检查是否修改了学号，因为学号是关联了user表的username的
        if 'student_number' in form.changed_data:
            student.user.username = form.cleaned_data['student_number']
            student.user.password = make_password(form.cleaned_data['student_number'][-6:])
            # 保存更改后的用户
            student.user.save()

        # 保存学生对象
        student.save()

        # 返回 JSON 响应
        return JsonResponse({
            'status': 'success',
            'message': '修改成功'
        }, status=200)

    # 表单验证失败后的处理逻辑
    def form_invalid(self, form):
        # 获取表单返回的错误信息
        errors = form.errors.as_json()
        return JsonResponse({
            'status': 'error',
            'message': errors
        }, status=400)

class StudentDeleteView(UpdateView):
    success_url = reverse_lazy('student_list')
    model =  Student

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            # 删除关联的 user 表中的数据
            self.object.user.delete()
            # 删除 student 表中的数据
            self.object.delete()
            return JsonResponse({
                'status': 'success',
                'message': '删除成功'
            }, status=200)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': '删除失败' + str(e)
            }, status=500)

class StudentBulkDeleteView(DeleteView):
    model =  Student
    success_url = reverse_lazy('student_list')

    def post(self, request, *args, **kwargs):
        student_ids = request.POST.getlist('student_ids')
        print(student_ids)
        if not student_ids:
            return JsonResponse({
                'status': 'error',
                'message': '请选择要删除的学生'
            }, status=400)
        self.object_list = self.get_queryset().filter(id__in=student_ids)
        try:
            for student in self.object_list:
                # 删除关联的 user 表中的数据
                student.user.delete()
                # 删除 student 表中的数据
            self.object_list.delete()
            return JsonResponse({
                'status': 'success',
                'message': '删除成功'
            }, status=200)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': '删除失败' + str(e)
            }, status=500)