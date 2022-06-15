from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Post

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
        cls.POST_EDIT = reverse('posts:post_edit', kwargs={
            'post_id': cls.post.id})

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
        users_login_reverse = reverse("users:login")
        post_create_reverse = reverse("posts:post_create")
        self.assertRedirects(
            response,
            f'{users_login_reverse}?next={post_create_reverse}',
            status_code=302,
        )
        self.assertEqual(Post.objects.count(), posts_count)

    def test_create_post(self):
        """Валидная форма создает запись Post."""
        post = Post.objects.first()
        post.delete()
        posts_count = Post.objects.count()
        form_data = {
            "text": "Тестовый текст",
        }
        response = self.authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response, reverse("posts:profile", kwargs={"username": "auth"})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post = response.context['page_obj'][0]
        self.assertEqual(post.text, form_data['text'])

    def test_edit_post(self):
        """Валидная форма редактирует запись Post."""
        posts_count = Post.objects.count()
        form_data = {
            "text": "Тестовый отредактированный текст",
        }
        response = self.authorized_client.post(
            self.POST_EDIT,
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse("posts:post_detail", kwargs={"post_id": 1})
        )
        self.assertEqual(Post.objects.count(), posts_count)
        post = response.context['post']
        self.assertEqual(post.author, self.post.author)
