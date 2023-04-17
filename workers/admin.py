from django.contrib import admin

from workers.models import Worker, WorkerLogs, WorkersTasks

admin.site.register(Worker)
admin.site.register(WorkerLogs)
admin.site.register(WorkersTasks)
