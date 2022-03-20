from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import CharField

User = get_user_model()


class Group(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self) -> CharField:
        return self.title


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Aвтор'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        help_text='Группа, к которой будет относиться пост'
    )

    def __str__(self):
        return self.text
