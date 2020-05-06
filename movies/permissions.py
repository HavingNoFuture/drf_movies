from rest_framework.permissions import BasePermission
from .services import get_client_ip_from_request


class IsIpOwner(BasePermission):
    def has_permission(self, request, view, *args, **kwargs):
        instance = view.get_object()
        try:
            return instance.ip == get_client_ip_from_request(request.user) or request.user.is_staff
        except:
            return False


class IsEmailOwner(BasePermission):
    def has_permission(self, request, view, *args, **kwargs):
        instance = view.get_object()
        try:
            return request.user.email == instance.email or request.user.is_staff
        except:
            return False
