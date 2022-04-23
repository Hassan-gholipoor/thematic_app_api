from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Category, Article, Comment
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
        elif self.action == 'upload_image':
            return serializers.ArticleImageSerializer
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

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        article = self.get_object()
        serializer = self.get_serializer(
            article,
            data=request.data
        )            
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class CommentViewset(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.CommentSerializer
    queryset = Comment.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return serializers.CommentDetailSerializer
        return self.serializer_class

    def get_queryset(self):
        return self.queryset.filter(author=self.request.user)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)