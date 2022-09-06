from app2.app.config import config
from commons.celery_worker.app import CustomTask, init_app

from .tasks.task1 import task1_

celery = init_app(config=config)


@celery.task(bind=True)
def task1(self: CustomTask, *args, **kwargs) -> str:
    return task1_(self, *args, **kwargs)
