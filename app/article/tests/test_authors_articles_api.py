from email.mime import multipart
from http import client
import tempfile
import os

from PIL import Image

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Article, Category, Comment
from article.serializers import ArticleSerializer, ArticleDetailSerializer


ARTICLE_URL = reverse('article:article-list')

def image_upload_url(article_id):
    return reverse('article:article-upload-image', args=[article_id])


def like_url(article_id):
    return reverse('article:article-add-like', args=[article_id])


def detail_url(pk):
    return reverse('article:article-detail', args=[pk])


class PrivateAuthorArticleApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.another_author_user = get_user_model().objects.create_author_user(
            'othermail@gmail.com',
            'testotherpassword'
        )
        self.author_user = get_user_model().objects.create_author_user(
            'authormail@gmail.com',
            'testpassword'
        )
        self.client.force_authenticate(self.author_user)

    def test_retreive_articles(self):
        cate1 = Category.objects.create(title='sport', slug='sport', author=self.author_user)
        cate2 = Category.objects.create(title='casual', slug='casual', author=self.author_user)
        article = Article.objects.create(
            title = 'A test article',
            description = 'Test description for above article',
            slug = 'SestSlug',
            owner=self.author_user
        )
        article.categories.set((cate1.id, cate2.id))

        res = self.client.get(ARTICLE_URL)

        articles = Article.objects.all()
        serializer = ArticleSerializer(articles, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_article_successful(self):
        cate1 = Category.objects.create(title='sport', slug='sport', author=self.author_user)
        payload = {
            "title": "Test Title",
            "description": "Description for test title",
            "slug": "Test",
            "categories": [cate1.id]
        }
        res = self.client.post(ARTICLE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        exists = Article.objects.filter(
            owner=self.author_user,
            title=payload['title'],
            description=payload['description'],
            slug=payload['slug']
        ).exists()
        self.assertTrue(exists)

    def test_create_article_invalid(self):
        payload = {
            "title": "",
        }
        res = self.client.post(ARTICLE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_view_article_detail(self):
        cate1 = Category.objects.create(title='sport', slug='sport', author=self.author_user)
        cate2 = Category.objects.create(title='casual', slug='casual', author=self.author_user)
        article = Article.objects.create(
            title = 'A test article',
            description = 'Test description for above article',
            slug = 'SestSlug',
            owner=self.author_user
        )
        article.categories.set((cate1.id, cate2.id))
        cm = Comment.objects.create(article=article, author=self.author_user, body="Hahaha Funny")
        url = detail_url(article.id)
        res = self.client.get(url)
        serializer = ArticleDetailSerializer(article)

        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_partials_updata_article(self):
        cate1 = Category.objects.create(title='sport', slug='sport', author=self.author_user)
        cate2 = Category.objects.create(title='casual', slug='casual', author=self.author_user)
        article = Article.objects.create(
            title = 'A test article',
            description = 'Test description for above article',
            slug = 'SestSlug',
            owner=self.author_user
        )
        article.categories.set((cate1.id, cate2.id))
        url = detail_url(article.id)

        payload = {
            "title": "New title for patch"
        }
        res = self.client.patch(url, payload)
        article.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(article.title, payload['title'])

    def test_full_update_article(self):
        cate1 = Category.objects.create(title='sport', slug='sport', author=self.author_user)
        cate2 = Category.objects.create(title='casual', slug='casual', author=self.author_user)

        article = Article.objects.create(
            title = 'A test article',
            description = 'Test description for above article',
            slug = 'SestSlug',
            owner=self.author_user
        )
        article.categories.set((cate1.id,))
        url = detail_url(article.id)

        payload = {
            "title":"New Title for puh updata",
            "description":"Changing article",
            "slug":"changed",
            "categories": [cate2.id]
        }
        res = self.client.put(url, payload)
        article.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(article.title, payload['title'])
        categories = article.categories.all()
        self.assertEqual(len(categories), 1)


    def test_retrieve_articles_filtered_by_catgories(self):
        cate1 = Category.objects.create(title='sport', slug='sport', author=self.author_user)
        cate2 = Category.objects.create(title='global', slug='global', author=self.author_user)
        article1 = Article.objects.create(
            title='A test title',
            description='a test description for a test article',
            slug='testTitle',
            owner=self.author_user,
        )
        article2 = Article.objects.create(
            title='Another Test Article',
            description='a test description for another test article',
            slug='anotherslug',
            owner=self.author_user,
        )
        article1.categories.set((cate1.id,))
        article2.categories.set((cate2.id,))

        res = self.client.get(ARTICLE_URL, {'categories': f'{cate1.id}'})

        serializer1 = ArticleSerializer(article1)
        serializer2 = ArticleSerializer(article2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)


class ArticleImageUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.author_user = get_user_model().objects.create_author_user(
            'authormail@gmail.com',
            'testpassauthor'
        )
        self.client.force_authenticate(self.author_user)
        cate1 = Category.objects.create(title='sport', slug='sport', author=self.author_user)
        self.article = Article.objects.create(
            title = 'A test article',
            description = 'Test description for above article',
            slug = 'SestSlug',
            owner=self.author_user
        )
        self.article.categories.set((cate1.id,))

    def test_upload_image_to_article(self):
        url = image_upload_url(self.article.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.article.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.article.image.path))

    def test_upload_image_bad_request(self):
        url = image_upload_url(self.article.id)
        res = self.client.post(url, {'image': 'not iamge'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class ArticleLikeAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.author_user = get_user_model().objects.create_author_user(
            'authormail@gmail.com',
            'testpassauthor'
        )
        self.client.force_authenticate(self.author_user)
        cate1 = Category.objects.create(title='sport', slug='sport', author=self.author_user)
        self.article = Article.objects.create(
            title = 'A test article',
            description = 'Test description for above article',
            slug = 'SestSlug',
            owner=self.author_user
        )
        self.article.categories.set((cate1.id,))

    def test_liking_article_successful(self):
        normal_user = get_user_model().objects.create_user(
            'testnormaluser@gmail.com',
            'testpassword'
        )
        self.article.like.set((normal_user.id,))
        url = like_url(self.article.id)
        payload = {
            'like': [self.author_user.id]
        }
        res = self.client.patch(url, payload)
        self.article.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('like', res.data)
        self.assertEqual(len(res.data['like']), 2)
        self.assertIn(self.author_user, self.article.like.all())
