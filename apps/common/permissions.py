from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_staff


class IsSeller(permissions.BasePermission):
    def has_permission(self, request, view):
        if (request.user.is_authenticated and request.user.account_type == 'SELLER' and request.user.seller.is_approved) or request.user.is_staff:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        return obj.seller == request.user.seller or request.user.is_staff