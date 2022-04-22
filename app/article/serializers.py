from rest_framework import serializers

from core.models import Category, Article, Comment
from user.serializers import UserSerializer


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('id', 'title', 'slug')
        read_only_fields = ('id',)


class AbbreviateCommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ('id', 'body', 'author', 'created_on')
        read_only_fields = ('id', 'author')


class ArticleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Article
        fields = ('id', 'title', 'description', 'slug', 'owner', 'categories', 'publish_date')
        read_only_fields = ('id', 'owner')


class ArticleDetailSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    comments = AbbreviateCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = ('id', 'title', 'description', 'slug', 'owner', 'categories', 'publish_date', 'comments')
        read_only_fields = ('id', 'owner')


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ('id', 'article', 'body', 'author', 'created_on')
        read_only_fields = ('id', 'author')


class CommentDetailSerializer(CommentSerializer):
    article = ArticleDetailSerializer(read_only=True)
    author = UserSerializer(read_only=True)