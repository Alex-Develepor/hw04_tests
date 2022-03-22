from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class FormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Test title',
            slug='test_slug',
            description='Test descrip'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test text',
        )

    def test_post(self):
        count_posts = Post.objects.count()
        form_data = {
            'text': 'Test text',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        post_1 = Post.objects.get(id=self.group.id)
        author_1 = User.objects.get(username='TestName')
        group_1 = Group.objects.get(title='Test title')
        self.assertEqual(Post.objects.count(), count_posts + 1)
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={
                'username': self.post.author
            }
        ))
        self.assertEqual(post_1.text, 'Test text')
        self.assertEqual(author_1.username, 'TestName')
        self.assertEqual(group_1.title, 'Test title')

    def test_authorized_edit_post(self):
        self.client.get(f'/posts/{self.post.id}/edit/')
        form_data = {
            'text': 'Another test text',
            'group': self.group.id
        }
        response = self.authorized_client.post(reverse(
            'posts:post_edit',
            kwargs={
                'post_id': self.post.id
            }),
            data=form_data,
            follow=True,
        )
        post_edit = Post.objects.get(id=self.group.id)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(post_edit.text, 'Another test text')
