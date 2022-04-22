from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Article, Category, Comment
from article.serializers import ArticleSerializer, ArticleDetailSerializer


AUTHOR_ARTICLES_URL = reverse('article:authors-articles-list')


def detail_url(pk):
    return reverse('article:authors-articles-detail', args=[pk])


class PublicAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        res = self.client.get(AUTHOR_ARTICLES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_users_must_author_to_access(self):
        user = get_user_model().objects.create_user(
            'testmail@gmail.com',
            'testpassword'
        )
        self.client.force_authenticate(user)
        res = self.client.get(AUTHOR_ARTICLES_URL)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


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

        res = self.client.get(AUTHOR_ARTICLES_URL)

        articles = Article.objects.all().order_by('-id')
        serializer = ArticleSerializer(articles, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
    
    def test_articles_limmited_to_author(self):
        cate1 = Category.objects.create(title='sport', slug='sport', author=self.author_user)
        cate2 = Category.objects.create(title='casual', slug='casual', author=self.author_user)
        article = Article.objects.create(
            title = 'A test article',
            description = 'Test description for above article',
            slug = 'SestSlug',
            owner=self.author_user
        )
        article.categories.set((cate1.id, cate2.id))

        cate3 = Category.objects.create(title='Sea News', slug='SeaNews', author=self.another_author_user)
        article2 = Article.objects.create(
            title = 'A new test article',
            description = 'Test description for above article',
            slug = 'newslug',
            owner=self.another_author_user
        )
        article.categories.set((cate3.id,))

        res = self.client.get(AUTHOR_ARTICLES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_create_article_successful(self):
        cate1 = Category.objects.create(title='sport', slug='sport', author=self.author_user)
        payload = {
            "title": "Test Title",
            "description": "Description for test title",
            "slug": "Test",
            "categories": [cate1.id]
        }
        res = self.client.post(AUTHOR_ARTICLES_URL, payload)

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
        res = self.client.post(AUTHOR_ARTICLES_URL, payload)

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

        res = self.client.get(AUTHOR_ARTICLES_URL, {'categories': f'{cate1.id}'})

        serializer1 = ArticleSerializer(article1)
        serializer2 = ArticleSerializer(article2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)
