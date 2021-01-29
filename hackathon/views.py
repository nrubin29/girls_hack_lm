from django.contrib.auth import authenticate, login as django_login
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse

from hackathon.models import HackathonUser


def home(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('problem'))

    return HttpResponseRedirect(reverse('login'))


def login(request):
    if request.method == 'POST':
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user and user.is_authenticated and user.is_active:
            django_login(request, user)
            return HttpResponseRedirect(reverse('problem'))

    template = loader.get_template('login.html')
    context = {}
    return HttpResponse(template.render(context, request))


def problem(request):
    template = loader.get_template('problem.html')
    context = {
        'me': HackathonUser.objects.get(user=request.user)
    }
    return HttpResponse(template.render(context, request))
