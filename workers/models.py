import datetime
import pytz
from django.db import models
from django.utils import timezone

from users.models import UserAccount
from companies.models import Company, Task, Qualification


# TODO: можливість співробітниками компанії отримувати фідбек від роботодавця щодо своїх завдань через мобільний додаток
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
    LOG_TYPES = [
        ('TA', 'Task appointed'),
        ('TD', 'Task done'),
        ('OC', 'Out of working place'),
        ('CL', 'Custom log'),
    ]
    date = models.DateField(null=False, auto_now_add=True)
    time = models.TimeField(null=False, auto_now_add=True)
    datetime = models.DateTimeField(null=False, auto_now_add=True)
    type = models.CharField(max_length=2, null=False, choices=LOG_TYPES, default='CL')
    description = models.TextField(null=True, blank=True)

    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, null=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return f"{self.date}({self.time})"


class TaskAppointment(models.Model):
    is_done = models.BooleanField(default=False, null=True, blank=True)
    difficulty_for_worker = models.FloatField(default=1, null=True, blank=True)
    time_start = models.DateTimeField(auto_now_add=True, null=False)
    time_end = models.DateTimeField(null=True, blank=True)

    task_appointed = models.ForeignKey(Task, on_delete=models.CASCADE, null=False)
    worker_appointed = models.ForeignKey(Worker, on_delete=models.CASCADE, null=False)

    def save(self, *args, **kwargs):
        if self.difficulty_for_worker:
            qualification = self.worker_appointed.qualification.modifier
            difficulty = self.task_appointed.difficulty.modifier
            self.difficulty_for_worker = difficulty / qualification
        super().save(*args, **kwargs)

    def get_task_performance(self) -> float:
        """
        Function counts performance of worker in completed task
        by calculating time spent on task without overtimes
        and dividing estimate_hours by gotten value
        """
        if self.is_done:
            time_start = timezone.localtime(self.time_start, pytz.timezone(self.worker_appointed.employer.timezone))
            time_end = timezone.localtime(self.time_end, pytz.timezone(self.worker_appointed.employer.timezone))
            worker_day_start = datetime.datetime.combine(datetime.date.today(), self.worker_appointed.day_start)
            worker_day_end = datetime.datetime.combine(datetime.date.today(), self.worker_appointed.day_end)

            task_timediff = time_end - time_start
            days_on_task = time_end.day - time_start.day
            if time_end.day != time_start.day:
                worker_timediff = datetime.timedelta(days=1) - (worker_day_end - worker_day_start)
                task_timediff = task_timediff - (worker_timediff * days_on_task)
                if time_end.time() > worker_day_end.time():
                    overtime = datetime.datetime.combine(datetime.date.today(), time_end.time()) - worker_day_end
                    task_timediff = task_timediff - overtime
            elif time_end.time() > worker_day_end.time():
                overtime = datetime.datetime.combine(datetime.date.today(),  time_end.time()) - worker_day_end
                task_timediff = task_timediff - overtime

            return self.task_appointed.estimate_hours / (task_timediff.total_seconds() / 3600)

        return self.worker_appointed.productivity

    def __str__(self):
        return f"{self.task_appointed.title} for {self.worker_appointed.username}"


class WorkerTaskComment(models.Model):
    time_created = models.DateTimeField(auto_now_add=True)
    text = models.TextField(null=False)

    task_appointment = models.ForeignKey(TaskAppointment, on_delete=models.CASCADE, null=False, related_name='comments')
