from .common import send_report
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
for hour in (6, 12, 18, 21):
    scheduler.add_job(send_report, 'cron', hour=hour, minute=0, second=0)
scheduler.add_job(send_report, 'cron', hour=23, minute=59, second=0)
scheduler.start()
