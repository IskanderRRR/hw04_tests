from django import forms
from django.conf import settings as conf_settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

POSTS_PER_PAGE = conf_settings.POSTS_PER_PAGE
User = get_user_model()
TESTING_ATTEMPTS = 13


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание группы",
        )
        cls.group2 = Group.objects.create(
            title="Тестовая группа 2",
            slug="test-slug-2",
            description="Тестовое описание группы 2",
        )

        posts_list = []
        for i in range(TESTING_ATTEMPTS):
            posts_list.append(
                Post(author=cls.user,
                     text=f'Тестовый текст поста {i}',
                     id=i,
                     group=cls.group,
                     )
            )
        cls.post = Post.objects.bulk_create(posts_list)
        cls.index_url = (reverse("posts:index"), "posts/index.html")
        cls.group_url = (
            reverse("posts:group_posts", kwargs={"slug": cls.group.slug}),
            "posts/group_list.html",
        )
        cls.group_url_2 = (
            reverse("posts:group_posts", kwargs={"slug": cls.group2.slug}),
            "posts/group_list.html",
        )
        cls.profile_url = (
            reverse("posts:profile", kwargs={"username": cls.user.username}),
            "posts/profile.html",
        )
        cls.post_url = (
            reverse("posts:post_detail", kwargs={"post_id": cls.post[0].id}),
            "posts/post_detail.html",
        )
        cls.new_post_url = (
            reverse("posts:post_create"),
            "posts/create_post.html",
        )
        cls.edit_post_url = (
            reverse("posts:post_edit", kwargs={"post_id": cls.post[0].id}),
            "posts/create_post.html",
        )
        cls.paginated_urls = (cls.index_url, cls.group_url, cls.profile_url)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username="HasNoName")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            self.index_url,
            self.profile_url,
            self.post_url,
            self.new_post_url,
            self.edit_post_url,
            self.group_url,
        }
        for i in templates_pages_names:
            with self.subTest(reverse_name=i[0]):
                response = self.authorized_client.get(i[0])
                self.assertTemplateUsed(response, i[1])

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.post_url[0])
        first_object = response.context["post"]
        post_text = first_object.text
        post_group_title = first_object.group.title
        post_author_username = first_object.author.username
        self.assertEqual(post_text, "Тестовый текст поста 0")
        self.assertEqual(post_group_title, self.group.title)
        self.assertEqual(post_author_username, self.post[0].author.username)

    def test_edit_post_page_show_correct_context(self):
        """Шаблон /edit_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.edit_post_url[0])
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_create_post_page_show_correct_context(self):
        """Шаблон /create сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.new_post_url[0])
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self.user = User.objects.create_user(username='TestUser2')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Test group_2',
            slug='test-slug_2',
            description='Test description_2',
        )
        self.post = Post.objects.bulk_create(
            [
                Post(
                    text='Testing paginator',
                    author=self.user,
                    group=self.group,
                ),
            ] * TESTING_ATTEMPTS
        )

    def test_first_page_contains_ten_records(self):
        templates_pages_names = {
            reverse('posts:index'): POSTS_PER_PAGE,
            reverse('posts:group_posts',
                    kwargs={'slug': self.group.slug}):
            POSTS_PER_PAGE,
            reverse('posts:profile',
                    kwargs={'username': self.user.username}):
            POSTS_PER_PAGE,
        }
        for reverse_template, expected in templates_pages_names.items():
            with self.subTest(reverse_template=reverse_template):
                response = self.client.get(reverse_template)
                self.assertEqual(len(response.context['page_obj']), expected)

    def test_second_page_contains_three_records(self):
        all_posts = Post.objects.filter(
            author__username=self.user.username
        ).count()
        second_page_posts = all_posts - POSTS_PER_PAGE
        templates_pages_names = {
            reverse('posts:index'): second_page_posts,
            reverse('posts:group_posts',
                    kwargs={'slug': self.group.slug}): second_page_posts,
            reverse('posts:profile',
                    kwargs={'username': self.user.username}):
            second_page_posts,
        }
        for reverse_template, expected in templates_pages_names.items():
            with self.subTest(reverse_template=reverse_template):
                response = self.client.get(reverse_template + '?page=2')
                self.assertEqual(len(response.context['page_obj']), expected)
