from liker.starter import Starter

from QzoneLiker.celery import app as celery_app

@celery_app.task(bind=True)
def liker(self):
    starter = Starter()
    starter.start()
