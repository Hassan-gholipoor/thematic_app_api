from rest_framework import permissions


class AuthorAccessPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_anonymous == True:
            return False
        elif request.user.is_author:
            return True