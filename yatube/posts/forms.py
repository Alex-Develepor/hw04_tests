from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')
        labels = {
            'group': 'Группа',
            'text': 'Текст поста'}
        help_texts = {'group': 'Выберите группу', 'text': 'Введите ссообщение'}
