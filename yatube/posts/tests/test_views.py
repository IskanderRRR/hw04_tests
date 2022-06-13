from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import Post, Group

User = get_user_model()


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
        cls.posts = []
        for i in range(13):
            cls.posts.append(
                Post.objects.create(
                    author=cls.user,
                    text=f"Тестовый текст поста {i}",
                    group=cls.group,
                )
            )
        cls.post = Post.objects.get(id=1)
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
            reverse("posts:post_detail", kwargs={"post_id": cls.post.id}),
            "posts/post_detail.html",
        )
        cls.new_post_url = (
            reverse("posts:post_create"),
            "posts/create_post.html",
        )
        cls.edit_post_url = (
            reverse("posts:post_edit", kwargs={"post_id": cls.post.id}),
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

    def test_first_page_contains_ten_records(self):
        response = self.client.get(self.paginated_urls[0][0])
        self.assertEqual(len(response.context["page_obj"]), 10)

    def test_second_page_contains_three_records(self):
        response = self.client.get(self.paginated_urls[0][0] + "?page=2")
        self.assertEqual(len(response.context["page_obj"]), 3)

    def test_first_group_post_page_contains_ten_records(self):
        response = self.client.get(self.paginated_urls[1][0])
        self.assertEqual(len(response.context["page_obj"]), 10)

    def test_second_group_post_page_contains_three_records(self):
        response = self.client.get(self.paginated_urls[1][0] + "?page=2")
        self.assertEqual(len(response.context["page_obj"]), 3)

    def test_first_profile_list_page_contains_ten_records(self):
        response = self.client.get(self.paginated_urls[2][0])
        self.assertEqual(len(response.context["page_obj"]), 10)

    def test_second_profile_list_page_contains_three_records(self):
        response = self.client.get(self.paginated_urls[2][0] + "?page=2")
        self.assertEqual(len(response.context["page_obj"]), 3)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.post_url[0])
        first_object = response.context["post"]
        post_text = first_object.text
        post_group_title = first_object.group.title
        post_author_username = first_object.author.username
        self.assertEqual(post_text, "Тестовый текст поста 0")
        self.assertEqual(post_group_title, "Тестовая группа")
        self.assertEqual(post_author_username, "auth")

    def test_existing_post_some_pages(self):
        tests_pages = {
            self.index_url,
            self.group_url,
            self.profile_url,
            self.group_url_2,
        }
        for i in tests_pages:
            with self.subTest(page=i[0]):
                response = self.authorized_client.get(i[0])
                result = False
                for post in response.context["page_obj"]:
                    post_text = post.text
                    post_group_title = post.group.title
                    post_author_username = post.author.username
                    if (
                        post_text == "Тестовый текст поста 12"
                        and post_group_title == "Тестовая группа"
                        and post_author_username == "auth"
                    ):
                        result = True
                        break
                if post_group_title == "Тестовая группа 2":
                    self.assertFalse(result)
                else:
                    self.assertTrue(result)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон /post_edit сформирован с правильным контекстом."""
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
