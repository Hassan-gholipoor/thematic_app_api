from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Article, Category
from article.serializers import ArticleSerializer, ArticleDetailSerializer


ARTICLE_URL = reverse('article:article-list')


def detail_url(pk):
    return reverse('article:article-detail', args=[pk])


class PublicArticlesAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_retrieves_article(self):
        self.author_user = get_user_model().objects.create_author_user(
            'testauthor@gmail.com',
            'testauthorpass'
        )
        cate1 = Category.objects.create(title='sport', slug='sport', author=self.author_user)
        cate2 = Category.objects.create(title='global', slug='global', author=self.author_user)
        article = Article.objects.create(
            title='A test title',
            description='a test description for a test article',
            slug='testTitle',
            owner=self.author_user,
        )
        article.categories.set((cate1.id, cate2.id))

        res = self.client.get(ARTICLE_URL)

        articles = Article.objects.all().order_by('-id')
        serializer = ArticleSerializer(articles, many=True)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        
    def test_view_article_detail(self):
        self.author_user = get_user_model().objects.create_author_user(
            'testauthor@gmail.com',
            'testauthorpass'
        )
        cate1 = Category.objects.create(title='sport', slug='sport', author=self.author_user)
        cate2 = Category.objects.create(title='global', slug='global', author=self.author_user)
        article = Article.objects.create(
            title='A test title',
            description='a test description for a test article',
            slug='testTitle',
            owner=self.author_user,
        )
        article.categories.set((cate1.id, cate2.id))
        serializer = ArticleDetailSerializer(article)

        url = detail_url(article.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)