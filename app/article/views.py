from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Category, Article
from article import serializers
from article import permissions as CustomePermissions


class CategoryViewset(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, CustomePermissions.AuthorAccessPermission)
    serializer_class = serializers.CategorySerializer
    queryset = Category.objects.all()

    def get_queryset(self):
        return self.queryset.filter(author=self.request.user)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    
class ArticleViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    serializer_class = serializers.ArticleSerializer
    queryset = Article.objects.all()

    def _ids_to_intiger(self, string):
        return [int(str_id) for str_id in string.split(',')]

    def get_queryset(self):
        categories = self.request.query_params.get('categories')
        queryset = self.queryset
        if categories:
            cat_ids = self._ids_to_intiger(categories)
            queryset = queryset.filter(categories__id__in=cat_ids)
        
        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return serializers.ArticleDetailSerializer
        return self.serializer_class


class AuthorArticleAPIView(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, CustomePermissions.AuthorAccessPermission)
    serializer_class = serializers.ArticleSerializer
    queryset = Article.objects.all()

    def _ids_to_intiger(self, string):
        return [int(str_id) for str_id in string.split(',')]


    def get_serializer_class(self):
        if self.action == 'retrieve':
            return serializers.ArticleDetailSerializer
        return self.serializer_class

    def get_queryset(self):
        categories = self.request.query_params.get('categories')
        queryset = self.queryset
        if categories:
            cat_ids = self._ids_to_intiger(categories)
            queryset = queryset.filter(categories__id__in=cat_ids)
        
        return queryset.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
