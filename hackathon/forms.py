from django import forms

from hackathon.models import Submission


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        exclude = ()
