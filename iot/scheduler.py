from apscheduler.schedulers.background import BackgroundScheduler
import datetime
from django.utils import timezone

from iot.models import Supervisor
from workers.models import WorkerLogs, TaskAppointment


def update_inactive_iot(last_active_minutes=20):
    curr_time_tw_ago = timezone.now() - datetime.timedelta(minutes=last_active_minutes)
    iot = Supervisor.objects.filter(is_active=True, last_active__lt=curr_time_tw_ago)
    if iot:
        iot.update(is_active=False)
        if iot.worker:
            task = TaskAppointment.objects.filter(worker_appointed=iot.worker, is_done=False)
            if task:
                WorkerLogs.objects.create(task=task,
                                          worker=iot.worker,
                                          type='SL',
                                          description=f'Supervisor was inactive during {last_active_minutes} minutes!')
        print("Inactive IoTs detected and updated!")
    else:
        print("Inactive IoTs not detected!")


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_inactive_iot, "interval", minutes=1, id="iot_updater_1", replace_existing=True)
    scheduler.start()
    print("Scheduler started")
