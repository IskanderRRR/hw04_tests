from django.contrib.auth import get_user_model
from ..forms import PostForm
from ..models import Post
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост содержащий очень большое количество букв",
        )
        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_not_create_post(self):
        """Неавторизованный пользователь не может создать запись Post."""
        posts_count = Post.objects.count()
        form_data = {
            "text": "Тестовый текст, который не будет опубликован",
        }
        response = self.guest_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertRedirects(
            response,
            f'{reverse("users:login")}?next={reverse("posts:post_create")}',
            status_code=302,
        )
        self.assertEqual(Post.objects.count(), posts_count)

    def test_create_post(self):
        """Валидная форма создает запись Post."""
        posts_count = Post.objects.count()
        form_data = {
            "text": "Тестовый текст",
        }
        response = self.authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertRedirects(
            response, reverse("posts:profile", kwargs={"username": "auth"})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        author = User.objects.get(username="auth")
        self.assertTrue(
            Post.objects.filter(
                author=author,
                text="Тестовый текст",
            ).exists()
        )

    def test_edit_post(self):
        """Валидная форма редактирует запись Post."""
        posts_count = Post.objects.count()
        form_data = {
            "text": "Тестовый отредактированный текст",
        }
        response = self.authorized_client.post(
            reverse("posts:post_edit", args=("1",)),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response, reverse("posts:post_detail", kwargs={"post_id": 1})
        )
        self.assertEqual(Post.objects.count(), posts_count)
        author = User.objects.get(username="auth")
        self.assertTrue(
            Post.objects.filter(
                author=author,
                text="Тестовый отредактированный текст",
            ).exists()
        )
