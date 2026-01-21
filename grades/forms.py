from django import forms
from .models import Grade

class GradeForm(forms.ModelForm):

    class Meta:
        model = Grade
        fields = ['grade_name', 'grade_number']