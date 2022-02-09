from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class CustomUser(AbstractUser):

    class Role:
        USER = 'user'
        ADMIN = 'admin'
        MODERATOR = 'moderator'
        choices = [
            (USER, 'user'),
            (ADMIN, 'admin'),
            (MODERATOR, 'moderator'),
        ]

    bio = models.TextField(
        'Биография',
        blank=True,
    )
    email = models.EmailField(unique=True, blank=False, verbose_name='email')
    role = models.CharField(
        choices=Role.choices, default=Role.USER, max_length=20)
    confirmation_code = models.CharField(max_length=100)

    @property
    def is_user(self):
        return self.role == self.Role.USER

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_moderator(self):
        return self.role == self.Role.MODERATOR


class Genres(models.Model):
    name = models.CharField(max_length=300, verbose_name='Жанр')
    slug = models.SlugField(unique=True,
                            verbose_name='Слаг')

    def __str__(self):
        return {'name': self.name, 'slug': self.slug}

    class Meta:
        ordering = ('-name',)
        verbose_name_plural = 'Жанры'


class Categories(models.Model):
    name = models.CharField(max_length=256, verbose_name='Категория')
    slug = models.SlugField(unique=True, max_length=50,
                            verbose_name='Слаг')

    def __str__(self):
        return {'name': self.name, 'slug': self.slug}

    class Meta:
        ordering = ('-name',)
        verbose_name_plural = 'Категории'


class Title(models.Model):
    name = models.CharField(max_length=300,
                            verbose_name='Произведение')
    year = models.IntegerField(verbose_name='Год',
                               validators=[
                                   MinValueValidator(-4000),
                                   MaxValueValidator(datetime.now().year)
                               ])
    description = models.TextField(blank=True, verbose_name='Описание')
    category = models.ForeignKey(Categories, null=True,
                                 on_delete=models.SET_NULL,
                                 related_name='categories',
                                 verbose_name='Категория',
                                 )
    genre = models.ManyToManyField(Genres,
                                   blank=True, related_name='genres',
                                   verbose_name='Жанр')

    class Meta:
        ordering = ('-year',)
        verbose_name_plural = 'Произведения'


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='title_reviews',
        verbose_name='Произведение')
    text = models.TextField()
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='author_reviews',
        verbose_name='Автор')
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='Оценка')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации отзыва')

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['author', 'title'],
            name='uniq_review')]
        ordering = ('pub_date',)
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='review_comments',
        verbose_name='Отзыв')
    text = models.TextField()
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='author_comments',
        verbose_name='Автор')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации комментария')

    class Meta:
        ordering = ('pub_date',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
