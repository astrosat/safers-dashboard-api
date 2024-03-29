from rest_framework.permissions import BasePermission


class IsSelf(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        return user == obj


class IsSelfOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        return user.is_superuser or user == obj


class IsOwnerorAdmin(BasePermission):
    def has_permission(self, request, view):
        request_user = request.user
        view_user = view.user
        return request_user.is_superuser or request_user == view_user
