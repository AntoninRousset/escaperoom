import gevent
from django.apps import AppConfig


def say_hi():
    while True:
        gevent.sleep(2)
        print('hi')


class EscaperoomConfig(AppConfig):
    name = 'escaperoom'

    def ready(self):
        gevent.spawn(say_hi)
