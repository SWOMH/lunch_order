from datetime import datetime
from config import celery_app
from constant import CONSTANT
from telegram_cls import telegram
from celery.schedules import crontab
from database.bloc import database_order

@celery_app.on_after_configure.connect
def periodic_task(sender, **kwargs):
    sender.add_periodic_task(crontab(minute='*/5', hour='8-23'), send_message_in_group.s())

@celery_app.task(
    name='send_message_in_group',
    max_retries=3,
    default_retry_delay=5
)
def send_message_in_group():
    """Задача для отправки всех заказов в группу перед тем, как отправить заказ в айку"""
    
    try:
        orders = database_order.get_today_orders_formatted()
        
        if not orders:
            telegram.send_message("На сегодня заказов нет", id=CONSTANT.WORK_CHAT_ID)
            return
        
        message = "\n".join(orders)
        telegram.send_message(message, id=CONSTANT.WORK_CHAT_ID)
    except Exception as e:
        error_msg = f'Ошибка при формировании заказов: {str(e)}'
        print(error_msg)
        telegram.send_message(error_msg, id=CONSTANT.CHAT_ID)
        raise
