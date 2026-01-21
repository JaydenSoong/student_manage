from django.urls import path
from .views import GradeListView

urlpatterns = [
    path('list/', GradeListView.as_view(), name='grade_list'),
]