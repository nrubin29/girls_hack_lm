from django.contrib import admin

from .models import *

admin.site.register(HackathonUser)
admin.site.register(Submission)
admin.site.register(Grade)
