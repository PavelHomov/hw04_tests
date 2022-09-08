from django.db import models
from django.contrib.auth import get_user_model

from .constants import POSTS_SYMBOLS

User = get_user_model()


class Group(models.Model):
    """Модель Group."""
    title = models.CharField(
        verbose_name="Название группы",
        max_length=200,
        help_text="Введите название группы",
    )
    slug = models.SlugField(
        verbose_name="Slug группы",
        unique=True,
        help_text="Введите адрес группы",
    )
    description = models.TextField(
        verbose_name="Описание группы",
        help_text="Введите описание",
    )

    def __str__(self) -> str:
        """Метод вывода названия группы."""
        return self.title


class Post(models.Model):
    """Модель Post."""
    text = models.TextField(
        verbose_name="Текст поста",
        help_text="Введите текст поста",
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации",
        auto_now_add=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name="Автор",
        help_text="Укажите автора поста",
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name="Группа",
        help_text="Укажите группу",
    )

    def __str__(self) -> str:
        """Метод возвращает первые 15 символов поста."""
        return self.text[:POSTS_SYMBOLS]
