import json
import openpyxl
from pathlib import Path
from io import BytesIO

from django.views.generic import ListView, UpdateView, CreateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from django.db.models import Q

from .models import Score
from .forms import ScoreForm
from grades.models import Grade
from students.models import Student
from utils.handle_excel import ReadExcel

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
        # 使用父类的方法，获取所有成绩
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
    # 默认的 context 返回的 score 对象，由于我们还要在页面中使用 grade 对象，所以可以重写 get_context_data 方法
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 获取所有班级并添加到上下文对象
        context['grades'] = Grade.objects.all().order_by('grade_number')
        # 判断当前选中的班级，并添加到上下文对象中
        context['current_grade'] = self.request.GET.get('grade', '')
        return context

class ScoreUpdateView(ScoreBasicView, UpdateView):
    template_name = 'scores/form.html'
    form_class = ScoreForm

    # 表单验证成功后的处理逻辑
    def form_valid(self, form):

        # 保存成绩对象
        form.save()

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


class ScoreDeleteView(ScoreBasicView, DeleteView):
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            # 删除 score 表中的数据
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

class ScoreDeleteMultipleView(ScoreBasicView, DeleteView):
    def post(self, request, *args, **kwargs):
        score_ids = request.POST.getlist('score_ids')
        print(score_ids)
        if not score_ids:
            return JsonResponse({
                'status': 'error',
                'message': '请选择要删除的成绩信息'
            }, status=400)
        self.object_list = self.get_queryset().filter(id__in=score_ids)
        try:
            for score in self.object_list:
                # 删除 score 表中的数据
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

class ScoreDetailView(ScoreBasicView, DetailView):
    template_name = 'scores/detail.html'

def score_export(request):
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
        # 从数据库中查询学生成绩数据
        scores = Score.objects.filter(grade=grade)
        if not scores.exists():
            return JsonResponse({
                'status': 'error',
                'message': '没有该班级的成绩信息'
            }, status=404)

        # 操作 excel
        wb = openpyxl.Workbook()
        ws = wb.active
        # 添加标题行
        ws.append (['考试名称', '姓名', '班级', '学号', '语文', '数学', '英语'])
        for score in scores:
            ws.append([
                score.title,
                score.student_name,
                score.grade.grade_name,
                score.student_number,
                score.chinese_score,
                score.math_score,
                score.english_score
            ])
        # 将 excel 数据保存到内存中
        output = BytesIO()
        wb.save(output)
        wb.close()
        # 重置文件指针(游标)
        output.seek(0)
        # 设置响应
        response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="scores.xlsx"'
        return response


def score_import(request):
    # 导入成绩的功能使用POST请求
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
    if data[0] != ['考试名称', '姓名', '班级', '学号', '语文', '数学', '英语']:
        return JsonResponse({
            'status': 'error',
            'message': 'Excel 中成绩信息不是指定格式'
        }, status=400)
    # 写入到数据库，因为第一行是标题行，所以从第二行开始写入数据库
    for row in data[1:]:
        # 解析数据
        title, student_name, grade, student_number, chinese_score, math_score, english_score = row
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
        if not grade:
            return JsonResponse({
                'status': 'error',
                'message': '班级不能为空'
            }, status=400)
        # 检查学生姓名，班级，学号是否匹配
        grade = Grade.objects.get(grade_name=grade)
        student = Student.objects.get(student_name=student_name, student_number=student_number, grade=grade)
        if not student:
            return JsonResponse({
                'status': 'error',
                'message': f'班级为 {grade}, 学号为 {student_number} 的学生 {student_name} 不存在'
            }, status=400)
        # 写入到数据库中
        try:
            # 在 score 表中写入数据
            Score.objects.create(
                title=title,
                student_name=student_name,
                student_number=student_number,
                grade=grade,
                chinese_score=chinese_score,
                math_score=math_score,
                english_score=english_score,
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


class MyScoreListView(ListView):
    model = Score
    template_name = 'scores/my_score_list.html'