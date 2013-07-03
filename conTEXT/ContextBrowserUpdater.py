"""
 Context Browser Updater: now used to update the content frame and process actions received from it
 part of conTEXT Amarok script
 (c) 2006-2013 <camico@users.sourceforge.net>
 originally based on the Amarok Smart DJ plugin
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

import os
import time    
import urllib
import re
import logging

from ControllableThread import ControllableThread
from Observable import Observer

from common import LOGFILE, CFGFILE, popup, tounicode, run
from FileProcessor import FileProcessor

errorMissingInfo = "missing info"
searchAllTemporary = "SEARCH_ALL_TEMPORARY"
amarokUnknownAlbum = "Unknown Album"
jsSeparator = "<sep>"

imgPath = os.path.join(os.path.dirname(__file__), "img")


class ContextBrowserUpdater(ControllableThread, Observer):

    logger = logging.getLogger("ContextBrowserUpdater")

    def __init__(self,proxyObject,configObject):
        ControllableThread.__init__(self)
        self.config = configObject
        self.amarok = proxyObject
        self.observe(self.amarok)
        self.observe(self.amarok.player)
        self.observe(self.amarok.contextBrowser)
        self.observe(self.config)
        self.amarok_available_yet = False
        self.update = False
        self.contentUpdaterCode = file(os.path.join(os.path.dirname(__file__), "ContextBrowserUpdater.js")).read()
        self.has_injected = 0
        self.fp = FileProcessor(self.amarok, self.config)
        self.manualsearchsite = ""
        self.searchnow = ""
        if self.config["autoSearchSites"] == "":
            self.config["autoSearchSites"] = self.fp.getInitialSites()
            
        # # remove playlouder (conTEXT 2m)
        # self.config["autoSearchSites"] = re.sub('playlouder.com:(False|True) ', '', self.config["autoSearchSites"])

        self.browser = "kioclient exec"
        self.font = self.tryToReadFontFromKde() or "10pt sans-serif"
        self.fontcolor = self.tryToReadFontColorFromKde() or "0,0,0"
        self.logger.debug("using font \"%s\" and color \"%s\"", self.font, self.fontcolor)

        # self.searchMenuCode = self.searchMenuCode % (imgPath, self.font)
        self.artist = ""
        self.album = ""
        self.url = ""

    def tryToReadFontFromKde(self):
        try:
            if '.kde4/' in __file__:
                kdeconfig = file(re.sub('\.kde4/share.*', '.kde4/share/config/kdeglobals', __file__)).read()
            else:
                kdeconfig = file(re.sub('\.kde/share.*', '.kde/share/config/kdeglobals', __file__)).read()
            s = re.search("\[General\].*?font=(.*?)\n", kdeconfig, re.S)
            if s:
                font = s.group(1).split(',')
                fontName = re.sub('^Sans Serif', 'Sans-Serif', font[0], 0, re.IGNORECASE)
                fontSize = (int(font[1]) + 1) if fontName == 'Serif' or fontName == 'Sans-Serif' else font[1]
                         # don't know why but it seems we have to add 1pt for these two
                font = "%spt %s, sans-serif" % (fontSize, fontName)
                self.logger.debug("...successfully read FONT from kde config")
                return font
            else:
                raise Exception("pattern not found")
        except Exception, e:
            self.logger.debug("Failed to read FONT from kde config: %s", e)
            return False

    def tryToReadFontColorFromKde(self):
        try:
            if '.kde4/' in __file__:
                kdeconfig = file(re.sub('\.kde4/share.*', '.kde4/share/config/kdeglobals', __file__)).read()
            else:
                kdeconfig = file(re.sub('\.kde/share.*', '.kde/share/config/kdeglobals', __file__)).read()
            s = re.search("\[Colors:View\].*?ForegroundNormal=(.*?)\n", kdeconfig, re.S)
            if s:
                rgb = s.group(1)
                self.logger.debug("...successfully read COLOR from kde config")
                return rgb
            else:
                raise Exception("pattern not found")
        except Exception, e:
            self.logger.debug("Failed to read COLOR from kde config: %s", e)
            return False

    def processEvent(self, object, eventName, *args):
        # self.logger.debug("event: %s, %s", eventName, args)
        if eventName == "amaroKExit":
            self.kill(asynchronous=True)  # we kill ourselves
        if eventName == "amaroKAvailable":
            self.amarok_available_yet = True
        if eventName == "nowPlaying":
            self.update = True
            self.artist = args[0]
            self.album = args[1]
            self.url = args[2]
        if eventName == "getCommands":
            self.runCommand(args[0])
        if eventName == "configChange":
            self.config_changed()
        # if eventName == "stopped":
        #     self.has_injected = 0
    
    def run(self):
#         while not self.__finish: time.sleep(1)
        errMsg = "Something went wrong in the context browser updater. This is not your fault, but a bug in "\
                 "Amarok Reader. Please report the contents of the file %s to the developer.\n"\
                 "If this error persists, please delete the file %s and try again." % (LOGFILE, CFGFILE)
        try:
            self._run()
        except Exception, e:
            self.logger.exception("Something wrong in context browser monitor, process stopped %s %s", e, e.__class__)
            popup(errMsg)
        except:
            self.logger.exception("Something wrong in context browser monitor, process stopped")
            popup(errMsg)
    
    def _run(self):
        self.logger.debug("Context browser monitor starting")
        while not self.amarok_available_yet and not self.killed():
            time.sleep(1)
        self.logger.debug("Context browser monitor started")
        
        # timer = 0
        self.has_injected = self.performInjection()  # do once when we start

        while not self.killed():
            if self.update is False:
                time.sleep(1)
                continue
                    
            self.update = False  # we do this so we can rerun it on the next iteration ASAP
            self.has_injected = self.performInjection()
            
        # exit
        self.fp.cleanup()
        self.logger.debug("Context browser monitor exiting")

    def runCommand(self, args):
        if self.killed(): return
        try:
            searchnow, file2trash, file2edit, url, self.manualsearchsite, autosearchsites, filename, scrollpos = args.split('|')
            # self.logger.debug("manualsearchsite: " + self.manualsearchsite)
            
            if searchnow:
                self.fp.currentalbum = '<conTEXT:reinit>'
                self.searchnow = searchnow
                self.update = True
            if file2trash:
                file2trash = tounicode(file2trash)
                self.logger.debug("trash file: %s", file2trash)
                run("kioclient move", file2trash, "trash:/")
                self.update = True
            if file2edit:
                file2edit = tounicode(file2edit)
                run("kioclient exec", file2edit)
            if url:
                self.logger.debug("CLICKED URL: %s", url)
                run(self.browser, url)
            if self.manualsearchsite:
                self.fp.manualSearch(self.manualsearchsite)
                self.update = True
        
            # self.logger.debug(autosearchsites)
            if (not self.searchnow == searchAllTemporary or searchnow == searchAllTemporary) and autosearchsites != "":
                self.config["autoSearchSites"] = autosearchsites

            self.config["fileName"] = filename
            self.config["scrollPos"] = scrollpos

        except ValueError:
            return

    def performInjection(self):
        
        def escape_js(string):
            return string.replace("\\", "\\\\").replace("\"", "\\\"")
        
        def convert_newlines(string):
            return string.replace("\r", "").replace("\n", "<br>")
        
        if self.killed(): return 0
        
        songurl = urllib.unquote(self.url)

        searchMenuSetVars = 'searchSites="%s"; hideDomains="%s"; paramBasepath="%s"; paramFont="%s";' % (
            self.config['autoSearchSites'], self.fp.getHideDomains(), imgPath, self.font)

        # look for files and reviews
        manualsearchsite = self.manualsearchsite
        self.fp.setCSS("* { font: %s }"
                       "body { color: rgb(%s) }" % (self.font, self.fontcolor))
        self.fp.reInit()
        self.config["autoSearchSites"] = self.fp.initSearchSites(self.config["autoSearchSites"])
        # if not self.manualsearchsite:
        self.amarok.contextBrowser.evalJS(searchMenuSetVars)

        self.logger.debug("songurl: %s", songurl)
        numlocal = 0
        numonline = 0
        if songurl.startswith("file://"):
            numlocal = self.fp.findFiles(songurl.replace("file://", ""))

        artist = self.artist if not self.artist.startswith("http://") else ""
        album = self.album if self.album != amarokUnknownAlbum else ""

        if artist and album:
            numonline = self.fp.findOnlineReviews(artist, album)
        
            if manualsearchsite:
                if numonline == 0:
                    return self.has_injected
        else:
            if manualsearchsite:
                self.amarok.contextBrowser.evalJS(
                    'searchError("' + manualsearchsite + '", "' + errorMissingInfo + '")')
        
        if self.searchnow == searchAllTemporary:
            self.config["autoSearchSites"] = self.config["autoSearchSites"].replace("True", "False")
        self.searchnow = ""    

        self.logger.debug("num files: %s", self.fp.numFiles())

        if self.fp.numFiles() is 0:
            self.amarok.contextBrowser.evalJS('searchSites="'+self.config["autoSearchSites"]+'"')
            self.amarok.contextBrowser.evalJS('info(0)')
            return 1
        
        # statusbar message
        if not manualsearchsite:
            localfiles = ""
            if numlocal > 0:
                localfiles = " %s local file(s) and" % numlocal
            if not numonline == -1:  # (same album - no search - no change - no message)
                self.amarok.contextBrowser.showMessage(
                    "Amarok Reader found%s %s web review(s) for <b>%s</b>" % (localfiles, numonline, album))
        
        if self.killed(): return 0
        
        # encode/concatenate files
        originalfilenames = unicode("")
        filenames = unicode("")
        for i in range(self.fp.numFiles()):
            path = self.fp.fileName(i)
            opath = self.fp.originalFileName(i)
            # text = self.fp.fileText(i)
            if i < self.fp.numFiles() - 1:
                sep = jsSeparator
            else:
                sep = ''
            originalfilenames = originalfilenames + opath + sep
            filenames = filenames + path + sep

        filenames = escape_js(filenames)
        originalfilenames = escape_js(originalfilenames)

        # self.logger.debug(self.config["autoSearchSites"])
        self.logger.debug("injecting filename: %s, scrollpos: %s" % (self.config["fileName"], self.config["scrollPos"]))

        try:
            contentUpdaterCode = self.contentUpdaterCode % (filenames,
                                                            originalfilenames,
                                                            self.config["fileName"],
                                                            self.config["scrollPos"],
                                                            self.config["autoSearchSites"])
        except Exception:
            contentUpdaterCode = self.contentUpdaterCode % (filenames,
                                                            originalfilenames,
                                                            "",
                                                            self.config["scrollPos"],
                                                            self.config["autoSearchSites"])

        if self.killed():
            return 0

        # self.amarok.contextBrowser.evalJS(searchMenuSetVars + contentUpdaterCode)
        self.amarok.contextBrowser.evalJS(contentUpdaterCode)
        # self.amarok.contextBrowser.evalJS("refreshBox(-1, true);")

        if manualsearchsite:
            self.amarok.contextBrowser.evalJS('searchSuccess("'+manualsearchsite+'")')
            self.amarok.contextBrowser.evalJS('showFileWithName("'+manualsearchsite+'.html")')
                    
        return 2
                
    def config_changed(self):
        self.logger.debug("config changed")
        #self.amarok.contextBrowser.evalJS('refreshBox('+str(h)+',"'+str(n)+'")')
