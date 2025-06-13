from datetime import datetime
from config import celery_app
from constant import CONSTANT
from telegram_cls import telegram
from celery.schedules import crontab
from database.telegram import sync_database_connect

@celery_app.on_after_configure.connect
def periodic_task(sender, **kwargs):
    sender.add_periodic_task(crontab(minute=40, hour=10), send_message_in_group.s())
    sender.add_periodic_task(crontab(minute=0, hour=11), send_all_orders_today_message_in_group.s())

@celery_app.task(
    name='send_message_in_group',
    max_retries=3,
    default_retry_delay=5
)
def send_message_in_group():
    """Задача для отправки всех заказов в группу перед тем, как отправить заказ в айку"""
    
    try:
        orders = sync_database_connect.get_today_orders_formatted()
        
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


@celery_app.task(
    name='send_all_orders_today_message_in_group',
    max_retries=3,
    default_retry_delay=5
)
def send_all_orders_today_message_in_group():
    try:
        orders = sync_database_connect.get_today_orders()
        
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