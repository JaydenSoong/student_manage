from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

from .forms import LoginForm
from teachers.models import Teacher
from students.models import Student

# Create your views here.
def user_login(request):
    # 判断是否为 POST 请求
    if request.method == 'POST':
        # form 表单验证
        form = LoginForm(request.POST)
        # 验证失败
        if not form.is_valid():
            return JsonResponse({'status': 'error', 'message': '提交信息有误!'}, status=404)
        # 验证成功
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        role = form.cleaned_data.get('role')
        # 判断角色
        if role == 'teacher':
            try:
                # 查询教师信息是否存在
                teacher = Teacher.objects.get(phone_number=username)
                # 使用 Django 自带的功能验证用户名和密码,构造 user 对象
                user = authenticate(username=username, password=password)
                # 为 username 重新赋值，便于页面显示
                username = teacher.teacher_name
            except Teacher.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': '教师信息不存在'}, status=404)
        elif role == 'student':
            try:
                # 查询学生信息是否存在
                student = Student.objects.get(student_number=username)
                # 构造 user 对象
                user = authenticate(username=username, password=password)
                # 为 username 重新赋值，便于页面显示
                username = student.student_name
            except Student.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': '学生信息不存在'}, status=404)
        else:
            try:
                # 对于管理员账户，直接构建对象
                user = authenticate(username=username, password=password)
            except:
                return JsonResponse({'status': 'error', 'message': '管理员信息不存在'}, status=404)
        # print(user)
        # print('用户'+user)
        # 验证成功，返回 Json 数据
        if user is not None:
            if user.is_active:
                # 使用 Django 自带的功能实现登录
                login(request, user)
                # 登录成功后将信息存入 session
                request.session['user_role'] = role
                request.session['user_name'] = username
                return JsonResponse({'status': 'success', 'message': '登录成功', 'role': role})
            else:
                return JsonResponse({'status': 'error', 'message': '账户已经被禁用'}, status=403)
        else:
            # 处理登录失败的情况
            return JsonResponse({'status': 'error', 'message': '用户名或密码错误'}, status=404)

    return render(request, 'accounts/login.html')


# 退出功能
def user_logout(request):
    """退出功能"""
    if 'user_role' in request.session:
        del request.session['user_role']
    if 'user_name' in request.session:
        del request.session['user_name']
    logout(request)
    request.session.flush()
    return redirect('user_login')

def change_password(request):
    """修改密码"""
    if request.method == 'POST':
        print(request.POST)
        form = PasswordChangeForm(request.user, request.POST)
        print(form.is_valid())
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return JsonResponse({'status': 'success', 'message': '密码修改成功'})
        else:
            errors = form.errors.as_json()
            return JsonResponse({'status': 'error', 'message': errors})
    return render(request, 'accounts/change_password.html')
