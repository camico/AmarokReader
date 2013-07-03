#!/usr/bin/env python

# Controllable Thread
# imported from the metadata service libraries
# Manuel Amador (Rudd-O)
# under the GPL

from threading import Thread


class ControllableThread(Thread):
    """The ControllableThread is a subclass of Thread that provides new methods kill() and stop().
    In your run() method, you should periodically check if the thread has been killed with self.killed(),
    which will return True if another thread process your thread.  You can implement the stop() method,
    which will be called when your thread is killed(). Example implementation:

    def run(self):
        while not self.killed():
            ... do some stuff that should not take long

    def stop(self):
        ...do some cleanups
    """
    __killed = False

    def __init__(self):
        Thread.__init__(self)

    def killed(self):
        return self.__killed

    def kill(self, asynchronous=False):
        self.__killed = True
        if self.isAlive():
            self.on_kill()
            if asynchronous is False and not self.isDaemon():  # only join non-daemon threads
                self.join()

    def on_kill(self):
        """Implement this method to have something performed when the thread is explicitly killed.
        This will not be performed if the thread aborts due to an Exception or terminates its run() method on its own.
        """
        pass