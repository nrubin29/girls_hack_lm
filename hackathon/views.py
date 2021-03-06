import functools
from typing import Type
from zipfile import ZipFile

from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.db.models import Model
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse

from hackathon.forms import SubmissionForm, GradeForm, BonusImageForm
from hackathon.models import HackathonUser, Submission, Grader, Grade, BonusImage, Competitor


def require_user(model: Type[Model]):
    def require_model(view_func):
        def wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and model.objects.filter(django_user=request.user).exists():
                return view_func(request, *args, **kwargs)

            return HttpResponseRedirect(reverse('home'))

        return functools.wraps(view_func)(wrapped_view)

    return require_model


require_grader = require_user(Grader)
require_competitor = require_user(Competitor)


def home(request):
    if request.user.is_authenticated:
        if type(HackathonUser.get_for(request.user)) == Grader:
            return HttpResponseRedirect(reverse('grader'))

        return HttpResponseRedirect(reverse('competitor'))

    return HttpResponseRedirect(reverse('login'))


def login(request):
    if request.method == 'POST':
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user and user.is_authenticated and user.is_active:
            django_login(request, user)
            return HttpResponseRedirect(reverse('home'))

    template = loader.get_template('login.html')
    context = {}
    return HttpResponse(template.render(context, request))


def logout(request):
    django_logout(request)
    return HttpResponseRedirect(reverse('home'))


@require_competitor
def competitor(request):
    success = None
    errors = None

    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)

        if not form.is_valid():
            success = False
            errors = form.errors

        else:
            old_submission = Submission.objects.filter(team_id=request.POST['team'])
            if old_submission.exists():
                old_submission.delete()

            form.save()
            success = True

    me = HackathonUser.get_for(request.user)

    template = loader.get_template('competitor/problem.html')
    context = {
        'me': me,
        'success': success,
        'errors': errors,
        'has_submission': Submission.objects.filter(team=me.team).exists(),
        'page': 'problem',
    }
    return HttpResponse(template.render(context, request))


@require_competitor
def bonus_image(request):
    success = None
    errors = None

    if request.method == 'POST':
        form = BonusImageForm(request.POST, request.FILES)

        if not form.is_valid():
            success = False
            errors = form.errors

        else:
            old_bonus_image = BonusImage.objects.filter(competitor_id=request.POST['competitor'])
            if old_bonus_image.exists():
                old_bonus_image.delete()

            form.save()
            success = True

    me = HackathonUser.get_for(request.user)

    template = loader.get_template('competitor/bonus-image.html')
    context = {
        'me': me,
        'success': success,
        'errors': errors,
        'has_bonus_image': BonusImage.objects.filter(competitor=me).exists(),
        'page': 'bonus_image',
    }
    return HttpResponse(template.render(context, request))


@require_grader
def grader(request):
    template = loader.get_template('grader.html')
    context = {
        'me': HackathonUser.get_for(request.user),
        'submissions': Submission.objects.all(),
        'graded': 'graded' in request.GET,
    }
    return HttpResponse(template.render(context, request))


@require_grader
def grade(request, submission_id):
    submission = Submission.objects.get(id=submission_id)
    me = HackathonUser.get_for(request.user)
    try:
        old_grade = Grade.objects.get(submission=submission, grader=me)
    except Grade.DoesNotExist:
        old_grade = None

    errors = None

    if request.method == 'POST':
        form = GradeForm(request.POST, request.FILES)

        if form.is_valid():
            if old_grade:
                old_grade.delete()

            form.save()
            return HttpResponseRedirect(reverse('grader') + '?graded=true')

        else:
            errors = form.errors

    files = {}

    with ZipFile(submission.file.file) as zip_file:
        for inner_file in zip_file.infolist():
            if not inner_file.is_dir():
                with zip_file.open(inner_file.filename) as f:
                    files[inner_file.filename] = f.read().decode()

    template = loader.get_template('grade.html')
    context = {
        'me': me,
        'submission': submission,
        'files': files,
        'old_grade': old_grade,
        'errors': errors,
    }
    return HttpResponse(template.render(context, request))
