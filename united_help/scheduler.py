from apscheduler.schedulers.background import BackgroundScheduler

from united_help.services import get_workers_pids
from united_help.tasks import event_finished, event_start_tomorrow


def init_scheduler():
    __list = [True]
    if get_workers_pids('process.sh', __list=__list):
        print('init_scheduler True')
        scheduler = BackgroundScheduler()
        scheduler.add_job(event_finished, 'interval', minutes=5)
        scheduler.add_job(event_start_tomorrow, 'interval', minutes=1320)
        scheduler.start()
