from django.db.models.signals import post_save, post_delete, post_init
from django.dispatch import receiver

from workers.models import TaskAppointment, WorkerLogs, Worker, WorkerSchedule


@receiver(post_save, sender=TaskAppointment)
def task_done_log(sender, instance=None, created=True, **kwargs):
    if not created:
        if instance.is_done:
            WorkerLogs.objects.create(task=instance.task_appointed,
                                      worker=instance.worker_appointed,
                                      type='TD',
                                      description='Task was done by the worker.')

            worker = Worker.objects.get(id=instance.worker_appointed.id)
            worker.productivity = round(((worker.productivity + instance.get_task_performance()) / 2), 4)
            worker.save(update_fields=["productivity"])
        else:
            WorkerLogs.objects.create(task=instance.task_appointed,
                                      worker=instance.worker_appointed,
                                      type='TC',
                                      description=f'Task status was changed to "{instance.status}" by the worker.')


@receiver(post_save, sender=Worker)
def worker_created(sender, instance=None, created=True, **kwargs):
    if created:
        WorkerSchedule.objects.create(worker=instance)
