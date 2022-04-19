from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.conf import settings

class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.is_author = True
        user.save(using=self._db)
 
        return user

    def create_author_user(self, email, password, **extra_fields):
        user = self.create_user(email, password, **extra_fields)
        user.is_author = True

        user.save(using=self._db)
 
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_author = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = "email"


class Category(models.Model):
    title = models.CharField(max_length=122, unique=True)
    slug = models.SlugField(max_length=155, unique=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Article(models.Model):
    title = models.CharField(max_length=155)
    description = models.TextField()
    slug = models.SlugField(max_length=155, unique=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    categories = models.ManyToManyField(Category, related_name='articles')
    publish_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title