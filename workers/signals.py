from django.db.models.signals import post_save, post_delete, post_init
from django.dispatch import receiver

from workers.models import WorkersTasks, WorkerLogs, Worker


@receiver(post_save, sender=WorkersTasks)
def task_done_log(sender, instance=None, created=True, **kwargs):
    if not created:
        WorkerLogs.objects.create(task=instance.task_appointed,
                                  worker=instance.worker_appointed,
                                  type='TD',
                                  description='Task was done by the worker.')
        worker = Worker.objects.get(id=instance.worker_appointed.id)
        worker.productivity = round(((worker.productivity + instance.get_task_performance()) / 2), 4)
        worker.save(update_fields=["productivity"])
