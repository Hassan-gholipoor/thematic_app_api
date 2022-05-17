from rest_framework import permissions
from core.models import Article


class AuthorAccessPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        elif request.user.is_author:
            return True

    def has_object_permission(self, request, view, obj):
        if obj.owner == request.user or request.user.is_superuser:
            return True
