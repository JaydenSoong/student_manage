from django.urls import path
from .views import GradeListView, GradeCreateView, GradeUpdateView

urlpatterns = [
    path('', GradeListView.as_view(), name='grade_list'),
    # 这里由于使用的是Django自带的UpdateView，所以这里需要使用pk参数,所以参数名必须是pk，而不能是id。虽然id就是主键
    path('<int:pk>/update/', GradeUpdateView.as_view(), name='grade_update'),
    path('create/', GradeCreateView.as_view(), name='grade_create'),
]