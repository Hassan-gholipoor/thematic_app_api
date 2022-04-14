from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Category

from article.serializers import CategorySerializer


CATEGORY_URLS = reverse('article:category-list')


class PublicCategoryAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        res = self.client.get(CATEGORY_URLS)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_user_must_author_to_access(self):
        user = get_user_model().objects.create_user(
            'testuser@gmail.com',
            'testuserpassword'
        )
        self.client.force_authenticate(user)
        res = self.client.get(CATEGORY_URLS)
        
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class PrivateCategoryAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@gmail.com',
            'testpass'
        )
        self.author = get_user_model().objects.create_author_user(
            'author@gmail.com',
            'testpassword'
        )
        self.client.force_authenticate(self.author)

    def test_retrieve_categories(self):
        Category.objects.create(title='sport', slug='sport', author=self.author)
        Category.objects.create(title='global', slug='global', author=self.author)

        res = self.client.get(CATEGORY_URLS)

        categories = Category.objects.all().order_by('-id')
        serializer = CategorySerializer(categories, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_categories_limited_to_author_user(self):
        Category.objects.create(title='sport', slug='sport', author=self.user)
        category = Category.objects.create(title='casual', slug='casual', author=self.author)
        
        res = self.client.get(CATEGORY_URLS)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['title'], category.title)

    def test_create_tags_successful(self):
        payload = {
            'title': 'sport',
            'slug': 'sport'
        }
        self.client.post(CATEGORY_URLS, payload)

        exists = Category.objects.filter(
            author=self.author,
            title=payload['title'],
            slug=payload['slug']
        ).exists()
        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        payload = {'title': ''}
        res = self.client.post(CATEGORY_URLS, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        