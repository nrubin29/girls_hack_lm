"""
Creates competitor accounts from data in a JSON file.
The file should be placed in the project root.

Schema:
[
  {
    "school": "School name",
    "members": [
      "Name 1",
      "Name 2",
      ...
    ]
  },
  ...
]
"""

import json

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from hackathon.management.commands.util import generate_password
from hackathon.models import Competitor, Team


class Command(BaseCommand):
    help = 'Creates competitor accounts from data in a JSON file.'

    def handle(self, *args, **kwargs):
        result = []

        with open('competitors.json') as f:
            teams = json.load(f)

            for team_dict in teams:
                team_result = {'school': team_dict['school'], 'members': []}
                team = Team.objects.create(school=team_dict['school'])

                for member_name in team_dict['members']:
                    username = member_name.replace(' ', '_').replace('\'', '').replace('-', '_').lower()
                    password = generate_password()
                    django_user = User.objects.create_user(username, password=password)

                    Competitor.objects.create(name=member_name, django_user=django_user, team=team)
                    team_result['members'].append({'name': member_name, 'username': username, 'password': password})

                result.append(team_result)

        with open('competitor_accounts.json', 'w') as f:
            json.dump(result, f, indent=2)
