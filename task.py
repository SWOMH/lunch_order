from config import celery_app
from telegram_cls import telegram



@celery_app.task(
    name='seng_message_in_group',
    bind=True,
    max_retries=3,
    default_retry_delay=5
)
def seng_message_in_group():
    """Задача для отправки всех заказов в группу перед тем, как отправить заказ в айку"""
    try:
        ...
    except Exception as e:
        telegram.send_message(f'Проблема при отправки заранее всех заказов в чат группы\n\nОшибка:{e}')