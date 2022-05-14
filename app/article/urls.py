from django.urls import path, include
from rest_framework.routers import DefaultRouter

from article import views


router = DefaultRouter()
router.register('categories', views.CategoryViewset)
router.register('articles', views.ArticleViewSet)
router.register('comments', views.CommentViewset)


app_name = 'article'

urlpatterns = [
    path('', include(router.urls)),
]