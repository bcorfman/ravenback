from contextlib import contextmanager
from checkers import start_server
from multiprocessing import Process


@contextmanager
def serve_api():
    proc = Process(target=start_server)
    proc.start()
    yield proc
    proc.terminate()
