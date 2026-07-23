from django.db import models

# Create your models here.
from django.contrib.auth.models import User


class UserProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    keyword1 = models.CharField(
        max_length=50,
        blank=True
    )

    keyword2 = models.CharField(
        max_length=50,
        blank=True
    )

    keyword3 = models.CharField(
        max_length=50,
        blank=True
    )

    def __str__(self):

        return self.user.username


class BlogArticle(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    date = models.DateField()

    title = models.CharField(
        max_length=200
    )

    body = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        unique_together = (
            "user",
            "date"
        )

    def __str__(self):

        return self.title
