from django.contrib import admin
from django import forms
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _

from companies.models import Company, Qualification, Task


class CompanyAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].disabled = True
        self.fields['role'].initial = 'C'

    # def clean(self):
    #     cleaned_data = super().clean()
    #     raw_password = cleaned_data.get('password')
    #     cleaned_data['password'] = make_password(raw_password)
    #
    #     return cleaned_data

    class Meta:
        model = Company
        fields = '__all__'


class CompanyAdmin(admin.ModelAdmin):
    form = CompanyAdminForm
    # def get_form(self, request, obj=None, **kwargs):
    #     if obj is None:
    #         kwargs['form'] = CompanyAdminForm
    #     return super().get_form(request, obj, **kwargs)


class TaskAdminForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()

        if not Qualification.objects.filter(company=cleaned_data.get('company'), id=cleaned_data.get('difficulty').id).exists():
            raise forms.ValidationError(_('Matching error, you are probably trying to set one company and the qualifications of another!'))

        return cleaned_data

    class Meta:
        model = Task
        fields = '__all__'


class TaskAdmin(admin.ModelAdmin):
    form = TaskAdminForm


admin.site.register(Company, CompanyAdmin)
admin.site.register(Qualification)
admin.site.register(Task, TaskAdmin)
# admin.site.register(Supervisor)