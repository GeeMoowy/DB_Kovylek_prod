from django import forms
from .models import AttendanceRecord

class AttendanceRecordForm(forms.ModelForm):
    class Meta:
        model = AttendanceRecord
        fields = ['present', 'status', 'notes']
        widgets = {
            'student': forms.HiddenInput(),
            'repetition': forms.HiddenInput(),
            'present': forms.CheckboxInput(),
            'status': forms.Select(),
            'notes': forms.TextInput()
        }