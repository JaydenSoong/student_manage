from django import forms
from .models import Student

class StudentForm(forms.ModelForm):

    class Meta:
        model = Student
        fields = ['student_number', 'student_name', 'gender', 'grade', 'birthday', 'contact_number', 'address']