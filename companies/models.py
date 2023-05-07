from django.db import models
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

    def __str__(self):
        return f"{self.name}({self.company.name})"


class Task(models.Model):
    title = models.CharField(max_length=100, null=False)
    description = models.CharField(max_length=255, null=True)
    estimate_hours = models.IntegerField(null=False)

    difficulty = models.ForeignKey(Qualification, on_delete=models.CASCADE, null=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return f"{self.title}({self.company.name})"

# TODO: make IoT model logic
# class Supervisor(models.Model):
#     name = models.CharField(max_length=100, null=False)
#     is_active = models.BooleanField(default=False, null=True)
#
#     company = models.ForeignKey(Company, on_delete=models.CASCADE, null=False)
#     worker = models.ForeignKey(Worker, on_delete=models.CASCADE, null=True)
#
#     def __str__(self):
#         return self.name
