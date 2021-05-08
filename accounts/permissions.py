from rest_framework import permissions

class IsActor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.actor == request.user
