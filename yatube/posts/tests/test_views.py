from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class ViewsTestContext(TestCase):
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
        self.user = User.objects.create_user(username='TestName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_page_uses_correct_template_name(self):
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_list',
                kwargs={
                    'slug': 'test_slug'
                }
            ),
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={
                    'username': self.user
                }
            ),
            'posts/post_detail.html': reverse(
                'posts:post_detail',
                kwargs={
                    'post_id': self.post.pk
                }
            ),
            'posts/create_post.html': reverse(
                'posts:post_edit',
                kwargs={
                    'post_id': self.post.pk
                }
            )
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_context_correct(self):
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_group_0 = first_object.group.title
        self.assertEqual(post_text_0, 'Test another text')
        self.assertEqual(post_author_0, 'TestName2')
        self.assertEqual(post_group_0, 'Test another title')

    def test_group_list_context_correct(self):
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={
                'slug': 'test_another_slug'
            }
        ))
        first_object = response.context['group']
        group_title_0 = first_object.title
        group_slug_0 = first_object.slug
        self.assertEqual(group_title_0, 'Test another title')
        self.assertEqual(group_slug_0, 'test_another_slug')

    def test_profile_page_context_correct(self):
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={
                'username': 'TestName2'
            }
        ))
        first_object = response.context['page_obj'][0]
        post_text = first_object.text
        post_author = response.context['author'].username
        group_title = first_object.group.title
        self.assertEqual(group_title, 'Test another title')
        self.assertEqual(post_text, 'Test another text')
        self.assertEqual(post_author, 'TestName2')

    def test_post_detail_context_correct(self):
        response = self.authorized_client.get(reverse(
            'posts:post_detail',
            kwargs={
                'post_id': self.post_second.pk
            }
        ))
        first_object = response.context['post']
        post_text = first_object.text
        self.assertEqual(post_text, 'Test another text')

    def test_create_form_context_correct(self):
        response = self.authorized_client.get(reverse(
            'posts:post_create'
        ))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, form in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, form)

    def test_edit_post_context_correct(self):
        response = self.authorized_client.get(reverse(
            'posts:post_edit',
            kwargs={
                'post_id': self.post_second.pk
            }
        ))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, form in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, form)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Test title',
            slug='test_slug'
        )
        cls.post = []
        for i in range(13):
            cls.post = Post.objects.create(
                author=cls.user,
                text=f'Test text{i}',
                pub_date='01.11.1998',
                group=cls.group
            )

    def test_paginator_index_first_page(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), settings.COUNTLIST)

    def test_paginator_index_second_page(self):
        response = self.authorized_client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_paginator_group_list_first_page(self):
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={
                'slug': 'test_slug',
            }
        ))
        self.assertEqual(len(response.context['page_obj']), settings.COUNTLIST)

    def test_paginator_group_list_second_page(self):
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={
                'slug': 'test_slug',
            }
        ) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_paginator_profile_first_page(self):
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={
                'username': self.user,
            }
        ))
        self.assertEqual(len(response.context['page_obj']), settings.COUNTLIST)

    def test_paginator_profile_second_page(self):
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={
                'username': self.user,
            }
        ) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)
