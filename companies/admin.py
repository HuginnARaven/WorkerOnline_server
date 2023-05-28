from django.contrib import admin
from django import forms
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _
from import_export.admin import ExportActionMixin

from companies.models import Company, Qualification, Task


class CompanyAdmin(ExportActionMixin, admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['role'].initial = 'C'
        form.base_fields['role'].disabled = True
        form.base_fields['role'].required = False
        if obj:
            form.base_fields['password'].disabled = True
            form.base_fields['password'].required = False

        return form

    def save_model(self, request, obj, form, change):
        if not change:
            obj.password = make_password(obj.password)

        super().save_model(request, obj, form, change)


class TaskAdminForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()

        if not Qualification.objects.filter(company=cleaned_data.get('company'), id=cleaned_data.get('difficulty').id).exists():
            raise forms.ValidationError(_('Matching error, you are probably trying to set one company and the qualifications of another!'))

        return cleaned_data

    class Meta:
        model = Task
        fields = '__all__'


class TaskAdmin(ExportActionMixin, admin.ModelAdmin):
    form = TaskAdminForm


class QualificationAdmin(ExportActionMixin, admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            form.base_fields['company'].disabled = True
            form.base_fields['company'].required = False

        return form


admin.site.register(Company, CompanyAdmin)
admin.site.register(Qualification, QualificationAdmin)
admin.site.register(Task, TaskAdmin)
