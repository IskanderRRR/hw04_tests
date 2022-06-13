from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Test group',
            slug='test-slug',
            description='Test description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test text',
        )

    def test_group_name_is_group_title(self):
        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_post_name_is_correct(self):
        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))

    def test_verbose_name(self):
        post = PostModelTest.post
        group = PostModelTest.group
        field_verboses = {
            'post': {
                'text': 'Текст поста',
                'pub_date': 'date published'},

            'group': {
                'title': 'Заголовок',
                'slug': 'Slug',
                'description': 'Описание группы'},
        }
        for value, expected in field_verboses['post'].items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)
        for value, expected in field_verboses['group'].items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        post = PostModelTest.post
        group = PostModelTest.group
        field_help_texts = {
            'post': {
                'text': 'Введите текст поста'},
            'group': {
                'title': 'Дайте название группы',
                'slug': 'Дайте ключ адреса страницы',
                'description': 'Опишите группу'}
        }
        for value, expected in field_help_texts['post'].items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)
        for value, expected in field_help_texts['group'].items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)
