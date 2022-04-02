from django.db import models
from django.contrib.auth.models import User


class ConferenceName(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self) -> str:
        return self.name


class Conference(models.Model):
    conference = models.ForeignKey(
        ConferenceName, on_delete=models.PROTECT, related_name="conf_year")
    year = models.IntegerField()
    url = models.URLField()

    def __str__(self) -> str:
        return f"{self.conference} {self.year}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["conference", "year"],
                name="conference_unique"
            )
        ]


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
    memo = models.TextField(blank=True)
    added_at = models.DateTimeField()
