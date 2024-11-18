import logging
from apscheduler.schedulers.background import BackgroundScheduler
from app import create_app
from database.functions import synchronize_db_events

app = create_app()

logger = logging.getLogger(__name__)

def scheduled_task():
    with app.app_context():
        synchronize_db_events()

if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=scheduled_task, trigger="interval", seconds=60)
    scheduler.start()
    logger.info("Scheduler started")
    try:
        app.run(debug=True)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Scheduler shutdown")
