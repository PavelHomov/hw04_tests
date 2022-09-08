from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post, User


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='TestAuthor')
        cls.auth_user = User.objects.create_user(username='TestAuthUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый текст поста',
            group=cls.group,
        )
        cls.form = PostForm()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostCreateFormTests.auth_user)
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(PostCreateFormTests.author)

    def test_create_post(self):
        """Валидная форма создает запись в Posts."""
        post_count = Post.objects.all()
        post_count_set = set(post_count)
        form_data = {
            'text': 'Введенный в форму текст',
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile', kwargs={'username': self.auth_user.username}
            )
        )
        post_new = Post.objects.all()
        post_new_set = set(post_new)
        difference = post_new_set.difference(post_count_set)
        self.assertEqual(len(difference), 1)
        for QuerySet in difference:
            last_post = QuerySet
            self.assertEqual(last_post.text, form_data['text'])
            self.assertEqual(last_post.group.pk, form_data['group'])

    def test_author_edit_post(self):
        """Валидная форма изменяет запись в Posts."""
        post = Post.objects.get(id=self.group.pk)
        self.authorized_client_author.get(f'/posts/{post.pk}/edit/')
        form_data = {
            'text': 'Отредактированный в форме текст',
            'group': self.group.pk,
        }
        response = self.authorized_client_author.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        post_edit = Post.objects.get(id=self.group.pk)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(post_edit.text, form_data['text'])
        self.assertEqual(post_edit.group.pk, form_data['group'])
