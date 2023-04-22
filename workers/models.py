from django.db import models

from users.models import UserAccount
from companies.models import Company, Task, Qualification


class Worker(UserAccount):
    first_name = models.CharField(max_length=100, null=False)
    last_name = models.CharField(max_length=100, null=False)
    working_hours = models.IntegerField(default=0, null=False)
    productivity = models.FloatField(default=1, null=True, blank=True)
    salary = models.IntegerField(default=0, null=False)
    day_start = models.TimeField(null=False)
    day_end = models.TimeField(null=False)

    employer = models.ForeignKey(Company, on_delete=models.CASCADE, null=False)
    qualification = models.ForeignKey(Qualification, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}({self.username})"


class WorkerLogs(models.Model):
    date = models.DateField(null=False)
    time = models.TimeField(null=False)
    type = models.IntegerField(default=0, null=False)

    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return f"{self.date}({self.time})"


class WorkersTasks(models.Model):
    is_done = models.BooleanField(default=False, null=True, blank=True)
    difficulty_for_worker = models.FloatField(default=1, null=True, blank=True)
    time_start = models.DateTimeField(auto_now=True, null=False)
    time_end = models.DateTimeField(null=True, blank=True)

    task_appointed = models.ForeignKey(Task, on_delete=models.CASCADE, null=False)
    worker_appointed = models.ForeignKey(Worker, on_delete=models.CASCADE, null=False)

    def save(self, *args, **kwargs):
        if self.difficulty_for_worker:
            qualification = Worker.objects.get(id=self.worker_appointed.id).qualification.modifier
            difficulty = Task.objects.get(id=self.task_appointed.id).difficulty.modifier
            self.difficulty_for_worker = qualification / difficulty
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.task_appointed.title} for {self.worker_appointed.username}"
