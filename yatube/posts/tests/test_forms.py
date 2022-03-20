from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class FormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            author=User.objects.create_user(username='TestName1'),
            text='Test text',
            pub_date='01.11.1998',
            group=Group.objects.create(
                title='Test title',
                slug='test_slug'
            )
        )
        cls.post_second = Post.objects.create(
            author=User.objects.create_user(username='TestName2'),
            text='Test another text',
            pub_date='29.12.1998',
            group=Group.objects.create(
                title='Test another title',
                slug='test_another_slug'
            )
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='TestName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_new_post(self):
        post_count = Post.objects.count()
        self.post_third = Post.objects.create(
            author=User.objects.create_user(username='TestName3'),
            text='Test another text3',
            pub_date='29.12.1998',
            group=Group.objects.create(
                title='Test another title 3',
                slug='test_slug3'
            )
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Group.objects.filter(
                slug='test_slug3',
            ).exists()
        )

    def test_edit_post(self):
        response = self.authorized_client.get(reverse(
            'posts:post_edit',
            kwargs={
                'post_id': self.post_second.pk
            }
        ))
        first_object = response.context['form']
        first_object.text = 'Test5'
        post_text = first_object.text
        self.assertEqual(post_text, 'Test5')
