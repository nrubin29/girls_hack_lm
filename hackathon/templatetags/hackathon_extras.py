from django import template

from hackathon.models import Submission, Grader

register = template.Library()


@register.filter
def graded_by(submission: Submission, grader: Grader):
    return submission.grade_set.filter(grader=grader).exists()
