from django.test import TestCase
from django.contrib.auth import get_user_model


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
