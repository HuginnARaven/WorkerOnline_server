from django.contrib import admin

from companies.models import Company, Qualification, Task

admin.site.register(Company)
admin.site.register(Qualification)
admin.site.register(Task)
# admin.site.register(Supervisor)