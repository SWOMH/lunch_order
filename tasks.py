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
async def send_message_in_group():
    """Задача для отправки всех заказов в группу перед тем, как отправить заказ в айку"""
    try:
        orders = await database_order.get_today_orders_formatted()
        
        if not orders:
            await telegram.send_message("На сегодня заказов нет", id=CONSTANT.WORK_CHAT_ID)
            return
        
        # Объединяем все заказы в одно сообщение с разделителями
        message = "\n".join(orders)
        await telegram.send_message(message, id=CONSTANT.WORK_CHAT_ID)
    except Exception as e:
        telegram.send_message(f'Проблема при отправки заранее всех заказов в чат группы\n\nОшибка:{e}', id=CONSTANT.CHAT_ID)

