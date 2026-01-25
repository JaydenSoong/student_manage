import datetime
import json
from pathlib import Path
from io import BytesIO

from django.http import JsonResponse, HttpResponse
from pathlib import Path

from django.http import JsonResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

from .models import Student
from .forms import StudentForm
from grades.models import Grade
from utils.handle_excel import ReadExcel
import openpyxl

# Create your views here.
class StudentListView(ListView):
    model = Student
    template_name = 'students/list.html'
    context_object_name = 'students'
    paginate_by = 9

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

"""
定义一个方法完成批量导入学生信息的功能
"""
def import_student(request):
    # 导入学生的功能使用POST请求
    if request.method == 'POST':
        file = request.FILES.get('excel_file')
        # 判断文件是否上传
        if not file:
            return JsonResponse({
                'status': 'error',
                'message': '请上传Excel文件'
            }, status=400)
    # 判断文件类型是否是Excel文件
    ext = Path(file.name).suffix
    if ext.lower() != '.xlsx':
        return JsonResponse({
            'status': 'error',
            'message': '文件类型错误，请上传.xlsx格式的文件'
        }, status=400)

    # 使用之前定义的ReadExcel类读取Excel文件
    read_excel = ReadExcel(file)
    data = read_excel.get_data()
    if data[0] != ['班级', '姓名', '学号', '性别', '出生日期', '联系电话', '家庭住址']:
        return JsonResponse({
            'status': 'error',
            'message': 'Excel 中学生信息不是指定格式'
        }, status=400)
    # 写入到数据库，因为第一行是标题行，所以从第二行开始写入数据库
    for row in data[1:]:
        # 解析数据
        grade, student_name, student_number, gender, birthday, contact_number, address = row
        # 检查班级是否存在
        grade = Grade.objects.filter(grade_name=grade).first()
        # 检查班级是否填写
        if not grade:
            return JsonResponse({
                'status': 'error',
                'message': f'ddd{grade} 不存在'
            }, status=400)
        # 检测主要字段
        if not student_name:
            return JsonResponse({
                'status': 'error',
                'message': '学生姓名不能为空'
            }, status=400)
        if not student_number or len(student_number) != 8:
            return JsonResponse({
                'status': 'error',
                'message': '学号不能为空，且长度必须为8位'
            }, status=400)
        # 检查日期格式
        if not isinstance(birthday, datetime.datetime):
            return JsonResponse({
                'status': 'error',
                'message': '出生日期格式错误'
            }, status=400)
        # 判断学生信息是否已经存在
        if Student.objects.filter(student_number=student_number).exists():
            return JsonResponse({
                'status': 'error',
                'message': f'学号 {student_name} 已经存在'
            }, status=400)

        # 写入到数据库中
        try:
            # 判断 auth_user 表中是否存在该用户,不存在时创建该用户
            username = student_number
            users = User.objects.filter(username=username)
            if users.exists():
                user = users.first()
            else:
                user = User.objects.create_user(username=username, password=make_password(username[-6:]))
            # 在 student 表中写入数据
            Student.objects.create(
                grade=grade,
                student_name=student_name,
                student_number=student_number,
                gender= 'M' if gender == '男' else 'F',
                birthday=birthday,
                contact_number=contact_number,
                address=address,
                user=user
            )

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': '导入失败' + str(e)
            }, status=500)
    # 全部导入成功，返回成功信息
    return JsonResponse({
        'status': 'success',
        'message': '导入成功'
    }, status=200)

"""
定义导出学生信息到 excel 文件的方法
"""
def export_student(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        grade_id = data.get('grade')
        # 判断 grade_id 是否为空
        if not grade_id:
            return JsonResponse({
                'status': 'error',
                'message': '班级参数缺失'
            }, status=400)
        # 判断班级是否存在
        try:
            grade = Grade.objects.get(id=grade_id)
        except Grade.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': '班级不存在'
            }, status=404)
        # 从数据库中查询学生数据
        students = Student.objects.filter(grade=grade)
        if not students.exists():
            return JsonResponse({
                'status': 'error',
                'message': '没有该班级的学生信息'
            }, status=404)

        # 操作 excel
        wb = openpyxl.Workbook()
        ws = wb.active
        # 添加标题行
        ws.append(['班级', '姓名', '学号', '性别', '出生日期', '联系电话', '家庭住址'])
        for student in students:
            ws.append([
                student.grade.grade_name,
                student.student_name,
                student.student_number,
                '男' if student.gender == 'M' else '女',
                student.birthday,
                student.contact_number,
                student.address
            ])
        # 将 excel 数据保存到内存中
        output = BytesIO()
        wb.save(output)
        wb.close()
        # 重置文件指针(游标)
        output.seek(0)
        # 设置响应
        response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="students.xlsx"'
        return response
