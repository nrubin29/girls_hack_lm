from zipfile import ZipFile

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
    school = models.CharField(max_length=128)

    @property
    def score(self):
        score = 0

        try:
            score += Submission.objects.get(team=self).score
        except Submission.DoesNotExist:
            pass

        for competitor in self.competitor_set.all():
            try:
                bonus_image = BonusImage.objects.get(competitor=competitor)
                if bonus_image.approved:
                    score += 1
                    break
            except BonusImage.DoesNotExist:
                pass

        if not score:
            return '--'

        return score

    @property
    def member_names(self):
        return ', '.join(self.competitor_set.values_list('name', flat=True))

    def __str__(self):
        return f'{self.member_names} ({self.school})'


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
            return 0

        return sum(map(lambda grade: grade.score, grades)) / len(grades)

    @property
    def contents(self):
        files = {}

        with ZipFile(self.file.file) as zip_file:
            for inner_file in zip_file.infolist():
                if not inner_file.is_dir():
                    file_name = inner_file.filename.split('/')[-1]

                    if not file_name.startswith('.') and (file_name.endswith('.py') or file_name.endswith('.java')):
                        with zip_file.open(inner_file.filename) as f:
                            try:
                                files[inner_file.filename] = f.read().decode()
                            except UnicodeDecodeError:
                                files[inner_file.filename] = 'An error occurred while decoding this file.'

        return files

    def __str__(self):
        return f'{self.team} : {self.file.name}'


class Grade(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    grader = models.ForeignKey(Grader, on_delete=models.CASCADE)
    function = models.PositiveSmallIntegerField()
    function_comments = models.TextField(blank=True)
    creativity = models.PositiveSmallIntegerField()
    creativity_comments = models.TextField(blank=True)
    readability = models.PositiveSmallIntegerField()
    readability_comments = models.TextField(blank=True)
    implementation = models.PositiveSmallIntegerField()
    implementation_comments = models.TextField(blank=True)
    general_comments = models.TextField(blank=True)

    @property
    def score(self):
        return self.function + self.readability + self.implementation + self.creativity

    def __str__(self):
        return f'{self.submission.team} graded by {self.grader.name}'


class BonusImage(models.Model):
    competitor = models.ForeignKey(Competitor, on_delete=models.CASCADE)
    image = models.ImageField()
    approved = models.BooleanField(default=False)

    def __str__(self):
        return self.competitor.name


class Settings(models.Model):
    class Status(models.TextChoices):
        closed = 'C', 'Closed'
        open = 'O', 'Open'
        ended = 'E', 'Ended'

    status = models.CharField(choices=Status.choices, default='C', max_length=1)

    def __str__(self):
        return 'Settings'
