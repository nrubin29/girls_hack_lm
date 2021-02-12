import functools

from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse

from hackathon.forms import SubmissionForm
from hackathon.models import HackathonUser, Submission


def require_grader(view_func):
    def wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                me = HackathonUser.objects.get(user=request.user)

                if me.is_grader:
                    return view_func(*args, **kwargs)

            except HackathonUser.DoesNotExist:
                pass

        return HttpResponseRedirect(reverse('home'))

    return functools.wraps(view_func)(wrapped_view)


def home(request):
    if request.user.is_authenticated:
        if HackathonUser.objects.get(user=request.user).is_grader:
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


def competitor(request):
    success = None
    errors = None

    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            success = True

        else:
            success = False
            errors = form.errors

    template = loader.get_template('competitor.html')
    context = {
        'me': HackathonUser.objects.get(user=request.user),
        'success': success,
        'errors': errors,
    }
    return HttpResponse(template.render(context, request))


@require_grader
def grader(request):
    template = loader.get_template('grader.html')
    context = {
        'me': HackathonUser.objects.get(user=request.user),
        'submissions': Submission.objects.all(),
    }
    return HttpResponse(template.render(context, request))
