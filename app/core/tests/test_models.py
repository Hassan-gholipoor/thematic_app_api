from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='test@gmail.com', password='testpass'):
    return get_user_model().objects.create_user(email, password)

class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        email = 'test@gmail.com'
        password = 'testpass'
        user = get_user_model().objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_email_normalized(self):
        email = 'test@GMAIL.COM'
        user = get_user_model().objects.create_user(email=email, password='testpass')
        
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, password='testpass')

    def test_create_superuser(self):
        user = get_user_model().objects.create_superuser(email='test@gmail.com', password='testpass')

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_author)

    def test_create_new_authoruser(self):
        user = get_user_model().objects.create_author_user(email='test@gmail.com', password='testpass')

        self.assertTrue(user.is_author)

    def test_string_representation_for_category(self):
        category1 = models.Category.objects.create(title='sport', slug='sport', author=sample_user())

        self.assertEqual(str(category1), 'sport')

    def test_string_representaion_for_article(self):
        user = get_user_model().objects.create_author_user(
            email='authoruser@gmail.com',
            password='testauthorpassword',
            name='testname'
        )
        category = models.Category.objects.create(title='sport', slug='sport', author=user)

        article = models.Article.objects.create(
            title='Barcelona vs Real Madrid', 
            description='blah blah blah',
            slug='barmadrid',
            owner=user
            )
        article.categories.set((category.id,))

        self.assertEqual(str(article), 'Barcelona vs Real Madrid')

    @patch('uuid.uuid4')
    def test_article_file_name_uuid(self, mock_uuid):
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.article_image_file_path(None, 'myimage.jpg')

        expected_path = f'uploads/article/{uuid}.jpg'
        self.assertEqual(file_path, expected_path)

