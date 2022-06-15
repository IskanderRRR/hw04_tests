from http import HTTPStatus
from http.client import OK

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый текст поста",
        )
        cls.post_edit_url = f"/posts/{cls.post.id}/edit/"
        cls.public_urls = (
            ("/", "posts/index.html"),
            (f"/group/{cls.group.slug}/", "posts/group_list.html"),
            (f"/profile/{cls.user.username}/", "posts/profile.html"),
            (f"/posts/{cls.post.id}/", "posts/post_detail.html"),
        )
        cls.private_urls = (
            ("/create/", "posts/create_post.html"),
            (cls.post_edit_url, "posts/create_post.html"),
        )
        cls.unexisting_urls = "/unexisting_page/"

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username="HasNoName")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_for_unauthorised_users(self):
        """Страницы public доступны любому пользователю."""
        page_url_names = {
            "/": HTTPStatus.OK,
            f"/group/{self.group.slug}/": HTTPStatus.OK,
            f"/profile/{self.user.username}/": HTTPStatus.OK,
            f"/posts/{self.post.id}/": HTTPStatus.OK,
            "/unexisting_page/": HTTPStatus.NOT_FOUND
        }
        for page, expected_status in page_url_names.items():
            with self.subTest(page=page):
                response = self.guest_client.get(page).status_code
                self.assertEqual(response, expected_status)

    def test_create_url_exists_at_desired_location(self):
        """Страницы private доступны авторизованному пользователю."""
        page_url_private_names = {
            "/create/": HTTPStatus.FOUND,
            self.post_edit_url: HTTPStatus.FOUND
        }
        for page, expected_status in page_url_private_names.items():
            with self.subTest(page=page):
                response = self.guest_client.get(page).status_code
                self.assertEqual(response, expected_status)

    def test_post_edit_url_exists_at_desired_location_authorized(self):
        """Страница /posts/1/edit/ доступна авторизованному автору поста
        пользователю."""
        response = self.authorized_client.get(self.private_urls[1][0])
        self.assertEqual(response.status_code, OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            self.public_urls,
            self.private_urls,
        }
        for i in templates_url_names:
            for address, template in i:
                with self.subTest(address=address):
                    response = self.authorized_client.get(address)
                    self.assertTemplateUsed(response, template)
