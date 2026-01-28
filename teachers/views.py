from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from django.db.models import Q

from utils.premissions import RoleRequiredMixin
from .models import Teacher
from .forms import TeacherForm
from grades.models import Grade

# Create your views here.
class TeacherBaseView(RoleRequiredMixin):
    model = Teacher
    success_url = reverse_lazy('teacher_list')
    context_object_name = 'teachers'
    template_name = 'teachers/form.html'
    form_class = TeacherForm
    allowed_roles = ['admin',]

class TeacherListView(TeacherBaseView, ListView):
    template_name = 'teachers/list.html'
    paginate_by = 9

    # 重写 get_queryset 方法，添加搜索功能
    def get_queryset(self):
        # 使用父类的方法，获取所有学生
        queryset = super().get_queryset()
        grade_id = self.request.GET.get('grade')
        keywords = self.request.GET.get('search')

        if grade_id:
            queryset = queryset.filter(grade__pk=grade_id)
        if keywords:
            queryset = queryset.filter(
                Q(phone_number=keywords) |
                Q(teacher_name=keywords)
            )
        return queryset
    # 默认的 context 返回的 teacher 对象，由于我们还要在页面中使用 grade 对象，所以可以重写 get_context_data 方法
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 获取所有班级并添加到上下文对象
        context['grades'] = Grade.objects.all().order_by('grade_number')
        # 判断当前选中的班级，并添加到上下文对象中
        context['current_grade'] = self.request.GET.get('grade', '')
        return context

class TeacherCreateView(TeacherBaseView, CreateView):

    # 表单验证成功后的处理逻辑
    def form_valid(self, form):
        # grade 表和 user 表是一对一关联，所以接收手机号字段，来作为 user 的 username
        phone_number = form.cleaned_data['phone_number']

        # 检查是user表中否已存在该用户
        users = User.objects.filter(username=phone_number)
        if users.exists():
            user = users.first()
        else:
            # 如果不存在该用户，则创建该用户
            user = User.objects.create_user(username=phone_number, password=phone_number[-6:])
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

class TeacherUpdateView(TeacherBaseView, UpdateView):

    # 表单验证成功后的处理逻辑
    def form_valid(self, form):
        # 从表单中获取老师对象实例
        teacher = form.save(commit=False)
        # 检查是否修改了手机号，因为手机号是关联了user表的username的
        if 'phone_number' in form.changed_data:
            teacher.user.username = form.cleaned_data['phone_number']
            teacher.user.password = make_password(form.cleaned_data['phone_number'][-6:])
            # 保存更改后的用户
            teacher.user.save()

        # 保存学生对象
        teacher.save()

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

class TeacherDeleteView(TeacherBaseView, DeleteView):

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

