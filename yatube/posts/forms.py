from django.forms import ModelForm

from .models import Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        labels = {'group': 'Группа', 'text': 'Сообщение'}
        help_texts = {'group': 'Выберете группу', 'text': 'Введите сообщение'}
        fields = ['group', 'text']
