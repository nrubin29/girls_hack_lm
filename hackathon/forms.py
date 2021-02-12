from django import forms

from hackathon.models import Submission, Grade


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        exclude = ()


class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        exclude = ()
