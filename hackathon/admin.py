from django.contrib import admin

from .models import *

admin.site.register(Team)
admin.site.register(Competitor)
admin.site.register(Grader)
admin.site.register(Submission)
admin.site.register(Grade)
admin.site.register(BonusImage)
admin.site.register(Settings)
