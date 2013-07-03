#!/usr/bin/env python

"""
 conTEXT startup file
 (c) 2006-2013 <camico@users.sourceforge.net>
 heavily based on the Amarok Smart DJ plugin
 (c) 2005 Rudd-O <dragonfear@gmail.com>
 
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

# unconditional imports

import sys
import os
import signal  # this to make signals go to the main thread *always*
import time
import logging
import pickle

from common import *

sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))
sys.path.reverse()


#if not 'scripts-data' in os.path.abspath(os.curdir):
#	sys.exit("Please start this from within Amarok.")

from Observable import Observable
import amarok
from ContextBrowserUpdater import ContextBrowserUpdater
from amarok import amaroKProxy
from SignalQueue import SignalQueue, Empty


def setup_logging():
    if DEBUG:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.WARNING)

    formatter = logging.Formatter("%(levelname)s:%(name)s: %(message)s")

    try:
        os.mkdir(DATADIR)
    except OSError, e:
        if e.errno == 17:  # already exists
            pass
        else:
            popup("Amarok Reader can not create directory " + DATADIR + "\n"
                  "Please check you have write permissions there.")
    try:
        outputFile = file(LOGFILE, "a+b", 0)
    except:
        return

    if len(sys.argv) > 1 and sys.argv[1] == "-v":
        handler = logging.StreamHandler(outputFile)
        handler.setFormatter(formatter)
        logging.getLogger().addHandler(handler)
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(formatter)
        logging.getLogger().addHandler(handler)
    else:
        handler = logging.StreamHandler(outputFile)
        handler.setFormatter(formatter)
        logging.getLogger().addHandler(handler)


def finish_logging():
    logging.shutdown()

logger = logging.getLogger()
# end logging


# begin config
class ConfigObject(dict, Observable):
    def __init__(self):
        dict.__init__(self)
        Observable.__init__(self)
        self.load()

    def load(self):
        logger.debug("loading config")
        _config = {}
        try:
            f = open(CFGFILE, "r")
            _config = pickle.load(f)
            f.close()
            logger.debug("loaded config successfully")

        except IOError, e:
            _config = None
        except EOFError, e:
            _config = None
        if _config is None:
            logger.debug("could not load config, using defaults")
            _config = dict()
            _config["fileName"] = ""
            _config["saveOnlineReviews"] = True
            _config["scrollPos"] = 0
            _config["autoSearchSites"] = ""
            _config["hideDotCom"] = False
            _config["hideDotCoUk"] = False
            _config["hideDotDe"] = False
            _config["hideDotNet"] = False

        # we butter the loaded config items into us!
        for key, val in _config.iteritems():
            self[key] = val

    def save(self):
        logger.debug("saving config")

        _config = {}
        for key, val in self.iteritems():
            _config[key] = val

        os.umask(077)
        try:
            f = open(CFGFILE, "w")
            pickle.dump(_config, f)
            f.close()
        except:
            logger.exception("could not save config, continuing")

    def notifyChanged(self):
        self.save()
        self.broadcastEvent("configChange")

# end config


# main function
def _actual_main():
    # set up signal handlers
    signal_queue = SignalQueue()
    for sig in [signal.SIGINT, signal.SIGTERM]:
        signal_queue.trap(sig)

    # split in two
    pid = os.fork()
    if pid:  # the parent, we go as normal
        logger.debug("Parent process: forked.  PID: %s", os.getpid())
        while True:
            try:
                sig = signal_queue.get(block=True, timeout=1)
            except Empty:
                pid, status = os.waitpid(pid, os.WNOHANG)
                if pid:
                    if os.WCOREDUMP(status):
                        logger.debug("Child core dumped")
                    elif os.WIFSIGNALED(status):
                        logger.debug("Child got an unhandled signal %s", os.WTERMSIG(status))
                    elif os.WIFEXITED(status):
                        logger.debug("Child returned with return value %s", os.WEXITSTATUS(status))
                    else:
                        logger.debug("Child died with status %s", status)
                    break
                continue
            logger.debug("Parent process got signal %s, going down and letting child notice on its own", sig)
            break
        logger.debug("Parent process going down")

    else:  # child, we continue
        logger.debug("Child process: forked.  PID: %s", os.getpid())
        logger.info("conTEXT starting up normally")

        config = ConfigObject()

        amarokPath = os.path.split(os.path.abspath(os.curdir))[0]
        amarokObject = amaroKProxy(amarokPath)

        contextBrowserUpdater = ContextBrowserUpdater(amarokObject, config)
        contextBrowserUpdater.start()

        amarokObject.startMonitoring()

        logger.info("conTEXT successfully started")

        # now, we wait for impending doom

        def parentAlive():
            return os.getppid() != 1

        while parentAlive() and amarokObject.isAlive() \
            and contextBrowserUpdater.isAlive() \
            and signal_queue.qsize() < 1:
                # logger.debug("___|%s|___", sys.stdin.readline().strip())
                time.sleep(1)

        logger.debug("killing context browser monitor")
        contextBrowserUpdater.kill(asynchronous=True)

        logger.debug("waiting for context browser monitor")
        contextBrowserUpdater.kill()

        config.save()

        logger.info("conTEXT finished")


def main():
    setup_logging()
    logger.debug("args: %s", sys.argv)

    all_okay = True
    try:
        _actual_main()
    # 	except SystemExit,e:
    # 		if e == 0: sys.exit(0)
    # 		else: raise
    except:
        all_okay = False
        logger.exception("An error occurred while starting up.  PID: %s", os.getpid())
        popup(
            "An error occurred while starting up Amarok Reader. This is not your fault, but a bug in "
            "Amarok Reader. Please report the contents of the file %s to the developer." % LOGFILE)

    finish_logging()
    if not all_okay:
        sys.exit(2)


if __name__ == "__main__":
    main()
