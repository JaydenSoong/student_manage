from django.urls import path
from .views import (StudentListView, StudentCreateView, StudentUpdateView,
                    StudentDeleteView, StudentBulkDeleteView, import_student, export_student)

urlpatterns = [
    path('', StudentListView.as_view(), name='student_list'),
    path('create/', StudentCreateView.as_view(), name='student_create'),
    path('<int:pk>/update/', StudentUpdateView.as_view(), name='student_update'),
    path('<int:pk>/delete/', StudentDeleteView.as_view(), name='student_delete'),
    path('bulk_delete/', StudentBulkDeleteView.as_view(), name='student_bulk_delete'),
    path('import_student/', import_student, name='import_student'),
    path('export_student/', export_student, name='export_student')
]