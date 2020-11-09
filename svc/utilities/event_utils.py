from threading import Thread, Event

from svc.constants.home_automation import Automation


class MyThread(Thread):
    def __init__(self, event, sched_function, function_interval):
        Thread.__init__(self)
        self.stopped = event
        self.function = sched_function
        self.interval = function_interval

    def run(self):
        while not self.stopped.wait(self.interval):
            self.function()


# stop_event.set() will kill the process
def create_thread(state, fn, delay=Automation.TIME.THIRTY_SECONDS):
    stop_event = Event()
    state.STOP_EVENT = stop_event
    state.ACTIVE_THREAD = MyThread(stop_event, fn, delay)
    state.ACTIVE_THREAD.start()
