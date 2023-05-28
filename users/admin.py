from django.contrib import admin
from django.contrib.auth.hashers import make_password
from import_export.admin import ExportActionMixin

from users.models import UserAccount, TechSupportRequest

from django.contrib import admin


class UserAccountAdmin(ExportActionMixin, admin.ModelAdmin):

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['role'].initial = 'A'
        form.base_fields['role'].disabled = True
        form.base_fields['role'].required = False
        if obj:
            form.base_fields['password'].disabled = True
            form.base_fields['password'].required = False

        return form

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.filter(role='A')
        return qs

    def save_model(self, request, obj, form, change):
        # Apply make_password only when creating a new instance
        if not change:  # Checking if instance is being created
            obj.password = make_password(obj.password)

        super().save_model(request, obj, form, change)


class TechSupportRequestAdmin(ExportActionMixin, admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['user'].disabled = True
        form.base_fields['user'].required = False
        form.base_fields['title'].disabled = True
        form.base_fields['title'].required = False
        form.base_fields['description'].disabled = True
        form.base_fields['description'].required = False

        return form

    def has_add_permission(self, request):
        return False


admin.site.register(UserAccount, UserAccountAdmin)
admin.site.register(TechSupportRequest, TechSupportRequestAdmin)
