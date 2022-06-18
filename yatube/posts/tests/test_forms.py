import shutil
import tempfile

from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTest(TestCase):

    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.user = User.objects.create_user(username='auth')
        self.group = Group.objects.create(
            title='Test group',
            slug='test-slug',
            description='Test description',
        )
        self.post = Post.objects.create(
            author=self.user,
            text='Test text',
            group=self.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_group_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Another test',
            'group': self.group.id,
            'author_id': self.user.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             reverse('posts:profile',
                                     kwargs={'username': self.user}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(Post.objects.filter(
                         text=form_data['text'],
                         group=form_data['group']
                         ).get().text, form_data['text'])
        self.assertTrue(Post.objects.filter(text=form_data['text'],
                                            group=form_data['group']).exists())
        self.assertEqual(Post.objects.filter(
                         author=form_data['author_id'],
                         text=form_data['text'],
                         group=form_data['group']
                         ).get().group_id, form_data['group'])
        self.assertEqual(Post.objects.filter(
                         author=form_data['author_id'],
                         text=form_data['text'],
                         group=form_data['group']
                         ).get().author_id, form_data['author_id'])

    def test_edit_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст поста с группой',
            'group': self.group.id,
            'author_id': self.user.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             reverse('posts:post_detail',
                                     kwargs={'post_id': self.post.id}))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(Post.objects.filter(
                        text=form_data['text'],
                        group=form_data['group']).exists())
        self.assertEqual(Post.objects.filter(
                         text=form_data['text'],
                         group=form_data['group']
                         ).get().text, form_data['text'])
        self.assertEqual(Post.objects.filter(
                         author=form_data['author_id'],
                         text=form_data['text'],
                         group=form_data['group']
                         ).get().group_id, form_data['group'])
        self.assertEqual(Post.objects.filter(
                         author=form_data['author_id'],
                         text=form_data['text'],
                         group=form_data['group']
                         ).get().author_id, form_data['author_id'])

    def test_create_post_by_guest(self):
        form_data = {
            'text': 'Post from unauthorized client',
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        create_url = reverse('posts:post_create')
        login_url = reverse('users:login')
        self.assertRedirects(response, f'{login_url}?next={create_url}')

    def test_edit_post_by_guest(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Edited post from unauthorized client',
        }
        response = self.guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        edit_url = reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        login_url = reverse('users:login')
        self.assertRedirects(response, f'{login_url}?next={edit_url}')
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertNotEqual(self.post.text, form_data['text'])
