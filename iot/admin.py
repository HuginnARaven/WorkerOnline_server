from django.contrib import admin
from django import forms
from django.utils.translation import gettext_lazy as _

from iot.models import Supervisor, Offer


class OfferAdmin(admin.ModelAdmin):

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:  # Editing an existing instance
            form.base_fields['company'].disabled = True
            form.base_fields['address_of_delivery'].disabled = True
        return form


class SupervisorAdmin(admin.ModelAdmin):

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['last_active'].disabled = True

        return form


admin.site.register(Supervisor, SupervisorAdmin)
admin.site.register(Offer, OfferAdmin)
