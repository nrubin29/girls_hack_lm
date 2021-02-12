from django.contrib.auth.models import User
from django.db import models


class HackathonUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    is_grader = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Submission(models.Model):
    team = models.ForeignKey(HackathonUser, on_delete=models.CASCADE)
    file = models.FileField()

    def __str__(self):
        return self.team.name


class Grade(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    grader = models.ForeignKey(HackathonUser, on_delete=models.CASCADE)
    function = models.PositiveSmallIntegerField()
    readability = models.PositiveSmallIntegerField()
    design = models.PositiveSmallIntegerField()
    algorithm = models.PositiveSmallIntegerField()
    comments = models.TextField(blank=True)

    def __str__(self):
        return f'{self.submission.team.name} graded by {self.grader.name}'
