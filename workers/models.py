import datetime
import pytz
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from users.models import UserAccount
from companies.models import Company, Task, Qualification, TaskVoting


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

    def get_recommended_deadline_for_task(self, task: Task, time_start: datetime.datetime) -> datetime.datetime:
        estimate_hours_with_productivity = task.estimate_hours * self.productivity
        worker_day_start = datetime.datetime.combine(datetime.date.today(), self.day_start)
        worker_day_end = datetime.datetime.combine(datetime.date.today(), self.day_end)
        working_days_on_task = datetime.timedelta(hours=estimate_hours_with_productivity) / (worker_day_end - worker_day_start)
        approx_finsh_date = (time_start + datetime.timedelta(days=working_days_on_task))

        time_diff = approx_finsh_date - time_start

        dates_on_task = [time_start + datetime.timedelta(days=i) for i in range(time_diff.days + 1)]
        print(dates_on_task)
        worker_schedule = WorkerSchedule.objects.get(worker=self)
        for date in dates_on_task:
            if worker_schedule.is_weekend(date):
                approx_finsh_date += datetime.timedelta(days=1)

        return approx_finsh_date

    def count_remaining_working_hours(self):
        today = timezone.now()
        last_monday = today - datetime.timedelta(days=today.weekday())
        appointments = TaskAppointment.objects.filter(worker_appointed=self, time_start__gte=last_monday)
        count_remaining_working_hours = self.working_hours
        for a in appointments:
            count_remaining_working_hours -= a.task_appointed.estimate_hours
        return count_remaining_working_hours

    def __str__(self):
        return f"{self.first_name} {self.last_name}({self.username})"


class WorkerLogs(models.Model):
    LOG_TYPES = [
        ('TA', 'Task appointed'),
        ('TD', 'Task done'),
        ('TC', 'Task status changed'),
        ('OC', 'Out of working place'),
        ('SL', 'Supervisor connection lost'),
        ('CL', 'Custom log'),
    ]
    datetime = models.DateTimeField(null=False, auto_now_add=True)
    type = models.CharField(max_length=2, null=False, choices=LOG_TYPES, default='CL')
    description = models.TextField(null=True, blank=True)

    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, null=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=False)

    class Meta:
        verbose_name = _('worker`s log')
        verbose_name_plural = _('worker`s logs')

    def __str__(self):
        return f"{self.worker.username} {self.type} ({self.datetime})"


class WorkerSchedule(models.Model):
    monday = models.BooleanField(default=True)
    tuesday = models.BooleanField(default=True)
    wednesday = models.BooleanField(default=True)
    thursday = models.BooleanField(default=True)
    friday = models.BooleanField(default=True)
    saturday = models.BooleanField(default=True)
    sunday = models.BooleanField(default=True)

    worker = models.OneToOneField(Worker, on_delete=models.CASCADE, null=False, related_name="schedule")

    def is_weekend(self, weekday: datetime.datetime) -> bool:
        """
        This method check in workers`s schedule if given weekday weekend. It checks it in employer timezone.
        :param weekday: day of week to check
        :return: True if it is weekend False if it isn`t
        """
        localized_today_weekday = timezone.localtime(weekday, self.worker.employer.get_timezone()).weekday()
        match localized_today_weekday:
            case 0:
                return not self.monday
            case 1:
                return not self.tuesday
            case 2:
                return not self.wednesday
            case 3:
                return not self.thursday
            case 4:
                return not self.friday
            case 5:
                return not self.saturday
            case 5:
                return not self.sunday
            case _:
                return False

    def __str__(self):
        return f'Schedule of {self.worker.username}'


class TaskAppointment(models.Model):
    is_done = models.BooleanField(default=False, null=True, blank=True)
    difficulty_for_worker = models.FloatField(default=1, null=True, blank=True)
    time_start = models.DateTimeField(auto_now_add=True, null=False)
    time_end = models.DateTimeField(null=True, blank=True)
    deadline = models.DateTimeField(null=False)
    status = models.CharField(default="", null=True, blank=True)

    task_appointed = models.OneToOneField(Task, on_delete=models.CASCADE, null=False, related_name='task_appointment')
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

            dates_on_task = [time_start + datetime.timedelta(days=i) for i in range(task_timediff.days + 1)]
            worker_schedule = WorkerSchedule.objects.get(worker=self.worker_appointed)
            for date in dates_on_task:
                if worker_schedule.is_weekend(date) and days_on_task != 0:
                    days_on_task -= 1
                    task_timediff -= datetime.timedelta(days=1)

            if worker_schedule.is_weekend(time_end):
                task_day_start = datetime.datetime.combine(time_end.date(), time_start.time())
                task_day_end = datetime.datetime.combine(time_end.date(), time_end.time())
                task_timediff -= (task_day_end - task_day_start)

            if time_end.day != time_start.day:
                worker_timediff = datetime.timedelta(days=1) - (worker_day_end - worker_day_start)
                task_timediff = task_timediff - (worker_timediff * days_on_task)
                if time_end.time() > worker_day_end.time():
                    overtime = datetime.datetime.combine(datetime.date.today(), time_end.time()) - worker_day_end
                    task_timediff = task_timediff - overtime
            elif time_end.time() > worker_day_end.time():
                overtime = datetime.datetime.combine(datetime.date.today(), time_end.time()) - worker_day_end
                task_timediff = task_timediff - overtime
            if (task_timediff.total_seconds() / 3600) > 0:
                result = self.task_appointed.estimate_hours / (task_timediff.total_seconds() / 3600)
                return result

        return self.worker_appointed.productivity

    class Meta:
        verbose_name = _('task appointment')
        verbose_name_plural = _('tasks appointments')

    def __str__(self):
        return f"{self.task_appointed.title} for {self.worker_appointed.username}"


class WorkerTaskComment(models.Model):
    time_created = models.DateTimeField(auto_now_add=True)
    text = models.TextField(null=False)

    task_appointment = models.ForeignKey(TaskAppointment, on_delete=models.CASCADE, null=False, related_name='comments')
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, null=False, related_name='comments')

    class Meta:
        verbose_name = _('task comment')
        verbose_name_plural = _('tasks comments')

    def __str__(self):
        return f"{self.task_appointment.task_appointed.title} ({self.time_created})"


class TaskVote(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=False)
    score = models.IntegerField(null=False)

    voting = models.ForeignKey(TaskVoting, on_delete=models.CASCADE, null=False, related_name='votes')
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, null=False)

    class Meta:
        unique_together = ('worker', 'task', 'voting', 'score')
