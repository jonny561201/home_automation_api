import logging
import threading
from threading import Thread, Event


class MyThread(Thread):
    __instance = None

    def __init__(self):
        if MyThread.__instance is not None:
            raise Exception('Instance already exists!')
        else:
            Thread.__init__(self, daemon=True)
            MyThread.__instance = self
            self.stopped = Event()
            self.function = None
            self.started = False

    @staticmethod
    def get_instance():
        if MyThread.__instance is None:
            MyThread.__instance = MyThread()
        return MyThread.__instance

    def initialize(self, function):
        if self.started:
            raise Exception("Thread has already been started; cannot re-initialize.")
        else:
            self.function = function

    def start(self):
        if self.function is None:
            raise Exception("Thread must be initialized before starting")
        else:
            self.started = True
            super().start()

    def run(self):
        try:
            self.function()
        except Exception:
            logging.exception('Exception thrown invoking function')

    def stop(self):
        self.stopped.set()
        if threading.current_thread() is self:
            return

        try:
            self.join(5)
        except RuntimeError:
            logging.exception('RuntimeError while joining thread')
        else:
            if self.is_alive():
                logging.warning('Thread did not stop within timeout')
