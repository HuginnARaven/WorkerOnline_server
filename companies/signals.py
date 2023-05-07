from django.db.models.signals import post_save, post_delete, post_init
from django.dispatch import receiver

from config import settings
from workers.models import WorkersTasks, WorkerLogs


@receiver(post_save, sender=WorkersTasks)
def task_appoint_log(sender, instance=None, created=True, **kwargs):
    if created:
        WorkerLogs.objects.create(task=instance.task_appointed,
                                  worker=instance.worker_appointed,
                                  type='TA',
                                  description='Task was appointed to the worker.')

    # if not created:
    #     WorkerLogs.objects.create(task=instance.task_appointed,
    #                               worker=instance.worker_appointed,
    #                               type='TD',
    #                               description='Task was done by the worker.')