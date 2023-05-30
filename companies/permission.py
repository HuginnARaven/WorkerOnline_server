from rest_framework import permissions


class IsCompany(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.role == 'C':
            return True
        return False


class IsCompanyWorker(permissions.BasePermission):
    """
    Specifically for worker CRUD endpoint because in worker model company named employer
    """
    def has_permission(self, request, view):
        if request.user.role == 'C':
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if obj.employer.id == request.user.id:
            return True
        return False


class IsCompanyOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.role == 'C':
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if obj.worker.employer.id == request.user.id:
            return True
        return False
