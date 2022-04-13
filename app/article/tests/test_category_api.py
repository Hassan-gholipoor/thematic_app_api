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


class PrivateCategoryAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@gmail.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_categories(self):
        Category.objects.create(title='sport', slug='sport', author=self.user)
        Category.objects.create(title='global', slug='global', author=self.user)

        res = self.client.get(CATEGORY_URLS)

        categories = Category.objects.all().order_by('-id')
        serializer = CategorySerializer(categories, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_categories_limited_to_user(self):
        user2 = get_user_model().objects.create_user('other@gmail.com', 'testpassword')
        Category.objects.create(title='sport', slug='sport', author=user2)
        category = Category.objects.create(title='casual', slug='casual', author=self.user)
        
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
            author=self.user,
            title=payload['title'],
            slug=payload['slug']
        ).exists()
        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        payload = {'title': ''}
        res = self.client.post(CATEGORY_URLS, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        