from django.db import models
from django.contrib.auth.models import User


class ConferenceName(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name


class Conference(models.Model):
    conference = models.ForeignKey(ConferenceName, on_delete=models.PROTECT)
    year = models.IntegerField()
    url = models.URLField()

    def __str__(self) -> str:
        return f"{self.conference} {self.year}"


class Paper(models.Model):
    title = models.TextField()
    abstract = models.TextField()

    def __str__(self) -> str:
        return self.title


class ReferencePaper(Paper):
    url = models.URLField()
    published_at = models.ForeignKey(Conference, on_delete=models.PROTECT)


class UserPaper(Paper):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    memo = models.TextField()
