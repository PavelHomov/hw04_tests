from http import HTTPStatus

from django.test import TestCase, Client

from ..models import Group, Post, User


class PostURLTests(TestCase):
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
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTests.auth_user)
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(PostURLTests.author)

    def test_page_404(self):
        """Проверяем, запрос к несуществующей странице."""
        response = self.client.get('/page_404/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_url_exists_at_desired_location_for_anonymous(self):
        """Страница доступна любому пользователю."""
        url_names = (
            '/',
            f'/group/{self.group.slug}/',
            f'/profile/{self.author}/',
            f'/posts/{self.post.pk}/',
        )
        for address in url_names:
            with self.subTest():
                response = self.client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_exists_at_desired_location_for_auth_user(self):
        """Страница доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_exists_at_desired_location_for_author(self):
        """Страница доступна автору."""
        response = self.authorized_client_author.get(
            f'/posts/{self.post.pk}/edit/'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_url_redirect_anonymous_on_admin_login(self):
        """Страница /create/ перенаправляет анонимного пользователя."""
        response = self.client.get('/create/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/create/')

    def test_post_detail_url_redirect_anonymous_on_admin_login(self):
        """Страница /posts/1/edit/ перенаправляет анонимного пользователя."""
        response = self.client.get(
            f'/posts/{self.post.pk}/edit/', follow=True
        )
        self.assertRedirects(
            response, (
                f'/auth/login/?next=/posts/{self.post.pk}/edit/'
            )
        )

    def test_urls_uses_correct_template(self):
        """Проверяем, что URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.post.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.post.author}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client_author.get(address)
                self.assertTemplateUsed(response, template)

    def test_not_author_redirect_post_edit_on_post_detail(self):
        """Страница /posts/1/edit/ перенаправляет не автора."""
        response = self.authorized_client.get(
            f'/posts/{self.post.pk}/edit/', follow=True
        )
        self.assertRedirects(
            response, (
                f'/posts/{self.post.pk}/'
            )
        )
