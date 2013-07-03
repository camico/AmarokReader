#!/usr/bin/env python

# These classes handle the communication with Amarok.
# Well, currently, they just exchange some custom messages through stdin and stdout with main.js script.
#
# (c) 2013 <camico@users.sourceforge.net>
#
# originally based on python amarok 1.4 lib by
# Manuel Amador (Rudd-O) written on 2005-11-28
# under the GPL

from Observable import Observable

from threading import Thread
import select
import logging
import sys
import time

logger = logging.getLogger("amaroK Proxy")


class amaroKObject:
    objectName = None

    def __init__(self, parent):
        self.parent = parent


class amaroKPlayer(amaroKObject, Observable):
    objectName = "player"

    def __init__(self, parent):
        amaroKObject.__init__(self, parent)
        Observable.__init__(self)


class amaroKMonitor(amaroKObject, Thread):
    def __init__(self, parent, commChannel):
        amaroKObject.__init__(self, parent)
        Thread.__init__(self)
        self.setDaemon(True)
        self.commChannel = commChannel

    def run(self):
        self.parent.broadcastEvent("amaroKAvailable")
        po = select.poll()
        po.register(self.commChannel, select.POLLIN | select.POLLHUP | select.POLLERR | select.POLLPRI)
        while True:
            try:
                readyfds = po.poll(1000)  # wait one second
            except select.error, e:
                if e.args[0] == 4:
                    continue  # we were stopped, and now we're cont'ed
                else:
                    raise
            if not readyfds:
                continue  # spin because nothing good came out of this wait instance
            try:
                line = self.commChannel.readline().strip()
            except IOError, e:
                if e.errno == 5:
                    line = None  # we are exiting
                elif e.errno == 4:
                    continue  # we were stopped, and now we're cont'ed
                else:
                    raise
            if not line:
                # amarok sent us no event, probably because we received
                # a signal, so we just bail out of the loop
                logger.debug("Empty message, bailing out")
                self.parent.broadcastEvent("amaroKExit")
                break

            if line.startswith("nowPlaying"):
                command, artist, album, url = line.split("~~")
                self.parent.player.broadcastEvent(command, artist, album, url)

            elif line.startswith("getCommands"):
                command, args = line.split('~~')
                self.parent.player.broadcastEvent(command, args)
            else:
                self.parent.broadcastEvent("unknownEvent", line)


class amaroKContextBrowser(amaroKObject, Thread, Observable):
    objectName = "html-widget2"

    def __init__(self, parent, filepath):
        Thread.__init__(self)
        self.setDaemon(True)
        amaroKObject.__init__(self, parent)
        Observable.__init__(self)

    def run(self):
        while True:
            time.sleep(1)

    def evalJS(self, js):
        logger.debug("evalJS %s;", js[:300] + "...")
        self.feed(js.encode('utf-8') + ';', 'js')

    def showMessage(self, me):
        try:
            logger.debug("showMessage %s;", me[:300] + "...")
            me = me.encode('utf-8')
            self.feed(me, 'me')
        except Exception:
            pass

    def feed(self, content, kind):
        try:
            sys.stdout.write("/*<" + kind + ">*/" + content + "/*</" + kind + ">*/")
            sys.stdout.flush()
        except IOError, e:
            if e.errno == 32:
                logger.warn("Probably window was closed while searching? %s", e)
                pass
            else:
                raise e


class amaroKProxy(Observable):
    player = None
    monitor = None
    contextBrowser = None

    def __init__(self, path):
        Observable.__init__(self)
        self.player = amaroKPlayer(self)
        self.monitor = amaroKMonitor(self, sys.stdin)
        self.contextBrowser = amaroKContextBrowser(self, path)

    def startMonitoring(self):
        self.monitor.start()
        self.contextBrowser.start()

    def isAlive(self):
        return self.monitor.isAlive()


__all__ = ["amaroKProxy"]
