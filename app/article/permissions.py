from rest_framework import permissions


class AuthorAccessPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_author == True:
            return True