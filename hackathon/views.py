from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse

from hackathon.models import HackathonUser


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
    template = loader.get_template('competitor.html')
    context = {
        'me': HackathonUser.objects.get(user=request.user)
    }
    return HttpResponse(template.render(context, request))


def grader(request):
    template = loader.get_template('grader.html')
    context = {
        'me': HackathonUser.objects.get(user=request.user),
        'submissions': range(6),
    }
    return HttpResponse(template.render(context, request))
