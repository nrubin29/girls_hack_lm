"""Creates grader accounts."""

import json

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from hackathon.management.commands.create_competitor_accounts import generate_password
from hackathon.models import Grader


class Command(BaseCommand):
    help = 'Creates grader accounts.'

    def handle(self, *args, **kwargs):
        result = []

        for i in range(1, 13):
            username = f'sig{i}'
            password = generate_password()
            django_user = User.objects.create_user(username, password=password)
            Grader.objects.create(name=f'SIG Grader {i}', django_user=django_user)
            result.append({'username': username, 'password': password})

        with open('grader_accounts.json', 'w') as f:
            json.dump(result, f, indent=2)
