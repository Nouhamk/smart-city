import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore

# Import from the root level, not as a relative import
from backend.app import cron

logger = logging.getLogger(__name__)

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")

    # Schedule job to run every hour
    scheduler.add_job(
        cron.import_openmeteo_data,  # Use the correct function reference
        trigger=CronTrigger(minute="0"),  # Run at the top of every hour
        id="import_openmeteo_data",
        max_instances=1,
        replace_existing=True,
    )

    logger.info("Starting scheduler...")
    scheduler.start()