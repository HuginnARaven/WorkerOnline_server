from django.db import models
from django.utils.translation import gettext_lazy as _
import pytz

from users.models import UserAccount


class Company(UserAccount):
    TIMEZONE_CHOICES = zip(pytz.all_timezones, pytz.all_timezones)

    name = models.CharField(max_length=100, null=False)
    description = models.TextField(null=True, blank=True)
    timezone = models.CharField(max_length=255, default='UTC', choices=TIMEZONE_CHOICES)

    def __str__(self):
        return f"{self.name}({self.username}) ({pytz.timezone(self.timezone)})"

    def get_timezone(self):
        return pytz.timezone(self.timezone)


class Qualification(models.Model):
    name = models.CharField(max_length=100, null=False)
    modifier = models.IntegerField(default=1, null=False)

    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=False)

    class Meta:
        verbose_name = _('qualification')
        verbose_name_plural = _('qualifications')

    def __str__(self):
        return f"{self.name}({self.company.name})"


class Task(models.Model):
    title = models.CharField(max_length=100, null=False)
    description = models.CharField(max_length=255, null=True)
    estimate_hours = models.IntegerField(null=False)

    difficulty = models.ForeignKey(Qualification, on_delete=models.CASCADE, null=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=False)

    class Meta:
        verbose_name = _('task')
        verbose_name_plural = _('tasks')

    def __str__(self):
        return f"{self.title}({self.company.name})"
