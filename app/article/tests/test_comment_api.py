from genericpath import exists
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Comment, Article, Category
from article.serializers import CommentSerializer, CommentDetailSerializer


COMMENT_URL = reverse('article:comment-list')

def comment_detail(pk):
    return reverse('article:comment-detail', args=[pk])


class PublicCommentApiTests(TestCase):

    def setUp(self):
        self.cient = APIClient()

    def test_login_required(self):
        res = self.client.get(COMMENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateCommentAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'realauthor@gmail.com',
            'testauthor',
        )
        self.client.force_authenticate(self.user)
        self.author_user = get_user_model().objects.create_author_user(
            'authormail@gmail.com',
            'authorpassword'
        )

    def test_retrieve_comments(self):
        cate1 = Category.objects.create(title='sport', slug='sport', author=self.author_user)
        cate2 = Category.objects.create(title='casual', slug='casual', author=self.author_user)
        article = Article.objects.create(
            title = 'A test article',
            description = 'Test description for above article',
            slug = 'SestSlug',
            owner = self.author_user
        )
        article.categories.set((cate1.id, cate2.id))
        cm1 = Comment.objects.create(article=article, author=self.user, body='Good')
        res = self.client.get(COMMENT_URL)

        comments = Comment.objects.all().order_by('-id')
        serializer = CommentSerializer(comments, many=True)
        self.assertEqual(serializer.data, res.data)

    def test_retrieve_comments_limmited_to_user(self):
        cate1 = Category.objects.create(title='sport', slug='sport', author=self.author_user)
        cate2 = Category.objects.create(title='casual', slug='casual', author=self.author_user)
        article = Article.objects.create(
            title = 'A test article',
            description = 'Test description for above article',
            slug = 'SestSlug',
            owner = self.author_user
        )
        another_user = get_user_model().objects.create_user(
            'another@gmail.com',
            'testmailpass'
        )
        article.categories.set((cate1.id, cate2.id))
        cm1 = Comment.objects.create(article=article, author=self.user, body='Good')
        cm2 = Comment.objects.create(article=article, author=another_user, body='Bad')
        res = self.client.get(COMMENT_URL)

        self.assertEqual(len(res.data), 1)

    def test_creating_comment_successful(self):
        cate1 = Category.objects.create(title='sport', slug='sport', author=self.author_user)
        cate2 = Category.objects.create(title='casual', slug='casual', author=self.author_user)
        article1 = Article.objects.create(
            title = 'A test article',
            description = 'Test description for above article',
            slug = 'SestSlug',
            owner = self.author_user
        )
        article1.categories.set((cate1.id, cate2.id))

        comment_payload = {
            "article": article1.id,
            "body": "Test body"
        }
        res = self.client.post(COMMENT_URL, comment_payload)

        comments = Comment.objects.filter(
            body=comment_payload['body']
        ).exists()
        self.assertTrue(comments)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_article_invalid(self):
        comment_payload = {
            'body': '',
        }
        res = self.client.post(COMMENT_URL, comment_payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_comment_detail_page(self):
        cate1 = Category.objects.create(title='sport', slug='sport', author=self.author_user)
        cate2 = Category.objects.create(title='casual', slug='casual', author=self.author_user)
        article = Article.objects.create(
            title = 'A test article',
            description = 'Test description for above article',
            slug = 'SestSlug',
            owner = self.author_user
        )
        article.categories.set((cate1.id, cate2.id))
        cm = Comment.objects.create(article=article, author=self.user, body='Good Article')
        article.comments.set((cm,))

        url = comment_detail(cm.id)
        res = self.client.get(url)

        serializer = CommentDetailSerializer(cm)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


