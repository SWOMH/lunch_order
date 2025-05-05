from datetime import datetime
from config import celery_app
from telegram_cls import telegram
from celery.schedules import crontab



@celery_app.on_after_configure.connect
def periodic_task(sender, **kwargs):
    sender.add_periodic_task(crontab(minute='*/5', hour='8-23'), seng_message_in_group.s())




@celery_app.task(
    name='seng_message_in_group',
    bind=True,
    max_retries=3,
    default_retry_delay=5
)
def seng_message_in_group():
    """Задача для отправки всех заказов в группу перед тем, как отправить заказ в айку"""
    try:
        print(f'Задача отработала {datetime.now()}')
    except Exception as e:
        telegram.send_message(f'Проблема при отправки заранее всех заказов в чат группы\n\nОшибка:{e}')