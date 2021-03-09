import functools
from typing import Type
from zipfile import ZipFile

from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.db.models import Model
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse

from hackathon.forms import SubmissionForm, GradeForm, BonusImageForm
from hackathon.models import HackathonUser, Submission, Grader, Grade, BonusImage, Competitor, Settings


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
        if request.user.is_staff:
            return HttpResponseRedirect('/admin')

        elif type(HackathonUser.get_for(request.user)) == Grader:
            return HttpResponseRedirect(reverse('grader'))

        return HttpResponseRedirect(reverse('competitor'))

    return HttpResponseRedirect(reverse('login'))


def login(request):
    error = None

    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('home'))

    if request.method == 'POST':
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user and user.is_authenticated and user.is_active:
            if not user.is_staff:
                settings = Settings.objects.get()
                if settings.status == 'C':
                    error = 'You cannot log in at this time.'

            if not error:
                django_login(request, user)
                return HttpResponseRedirect(reverse('home'))

    template = loader.get_template('login.html')
    context = {
        'error': error
    }
    return HttpResponse(template.render(context, request))


def logout(request):
    django_logout(request)
    return HttpResponseRedirect(reverse('home'))


@require_competitor
def competitor(request):
    settings = Settings.objects.get()

    if settings.status == 'E':
        return end(request)

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


def end(request):
    me = HackathonUser.get_for(request.user)

    template = loader.get_template('competitor/end.html')
    context = {
        'me': me,
        'submission': Submission.objects.get(team=me.team),
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


@require_competitor
def schedule(request):
    template = loader.get_template('competitor/schedule.html')
    context = {
        'me': HackathonUser.get_for(request.user),
        'page': 'schedule',
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
        grade = Grade.objects.get(submission=submission, grader=me)
    except Grade.DoesNotExist:
        grade = None

    errors = None

    if request.method == 'POST':
        form = GradeForm(request.POST, request.FILES)

        if form.is_valid():
            if grade:
                grade.delete()

            form.save()
            return HttpResponseRedirect(reverse('grader') + '?graded=true')

        else:
            errors = form.errors

    template = loader.get_template('grade.html')
    context = {
        'me': me,
        'submission': submission,
        'grade': grade,
        'errors': errors,
    }
    return HttpResponse(template.render(context, request))
