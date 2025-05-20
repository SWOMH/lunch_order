import os
import ssl

from celery import Celery
from pydantic_settings import BaseSettings, SettingsConfigDict


redis_url = os.getenv('CELERY_BROKER_URL')


celery_app = Celery(
    "celery_worker",
    broker=redis_url,
    backend=redis_url
)

celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    enable_utc=True,
    timezone='Europe/Moscow',
    broker_connection_retry_on_startup=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)