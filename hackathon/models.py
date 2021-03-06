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

    @property
    def score(self):
        grades = list(self.grade_set.all())

        if not grades:
            return '--'

        return sum(map(lambda grade: grade.score, grades)) / len(grades)

    def __str__(self):
        return f'{self.team} : {self.file.name}'


class Grade(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    grader = models.ForeignKey(Grader, on_delete=models.CASCADE)
    function = models.PositiveSmallIntegerField()
    function_comments = models.TextField(blank=True)
    readability = models.PositiveSmallIntegerField()
    readability_comments = models.TextField(blank=True)
    implementation = models.PositiveSmallIntegerField()
    implementation_comments = models.TextField(blank=True)
    creativity = models.PositiveSmallIntegerField()
    creativity_comments = models.TextField(blank=True)
    educational = models.PositiveSmallIntegerField()
    educational_comments = models.TextField(blank=True)
    general_comments = models.TextField(blank=True)

    @property
    def score(self):
        return self.function + self.readability + self.implementation + self.creativity + self.educational

    def __str__(self):
        return f'{self.submission.team} graded by {self.grader.name}'
