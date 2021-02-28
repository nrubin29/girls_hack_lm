from django.contrib.auth.models import User
from django.db import models


class HackathonUser(models.Model):
    class Meta:
        abstract = True

    django_user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name

    @classmethod
    def get_for(cls, django_user: User):
        try:
            return Competitor.objects.get(django_user=django_user)
        except Competitor.DoesNotExist:
            try:
                return Grader.objects.get(django_user=django_user)
            except Grader.DoesNotExist:
                pass

        return None


class Team(models.Model):
    def __str__(self):
        return ', '.join(self.competitor_set.values_list('name', flat=True))


class Competitor(HackathonUser):
    team = models.ForeignKey(Team, on_delete=models.DO_NOTHING)


class Grader(HackathonUser):
    pass


class Submission(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    file = models.FileField()

    def __str__(self):
        return f'{self.team} : {self.file.name}'


class Grade(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    grader = models.ForeignKey(Grader, on_delete=models.CASCADE)
    function = models.PositiveSmallIntegerField()
    readability = models.PositiveSmallIntegerField()
    implementation = models.PositiveSmallIntegerField()
    creativity = models.PositiveSmallIntegerField()
    educational = models.PositiveSmallIntegerField()
    comments = models.TextField(blank=True)

    def __str__(self):
        return f'{self.submission.team} graded by {self.grader.name}'
