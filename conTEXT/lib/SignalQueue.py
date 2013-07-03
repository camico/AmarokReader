#!/usr/bin/env python

# Signal Queue
# Manuel Amador (Rudd-O) - written on 2005-11-29
# under the GPL

import os
from Queue import Queue, Empty
import logging

logger = logging.getLogger("SignalQueue")


class SignalQueue(Queue):
    def __init__(self):
        Queue.__init__(self)

    def handler(self, signal, frame):
        """The installable signal handler"""
        logger.info("%s received signal %s" % (os.getpid(), signal))
        self.put(signal)

    def trap(self, signal):
        from signal import signal as sigaction

        sigaction(signal, self.handler)
