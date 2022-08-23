import checkers
from threading import Thread
from waitress import serve


def waitress_serve_api():
    thread = Thread(target=serve, args=(checkers.__hug_wsgi__,), kwargs={'host': "127.0.0.1", 'port': 8000})
    thread.start()
