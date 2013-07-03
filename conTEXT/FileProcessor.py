"""
 File Processor: finds and processes text files and web reviews
 part of conTEXT Amarok script
 (c) 2006-2013 <camico@users.sourceforge.net>
 
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

import os, re, logging, httplib, urllib, string
from common import *
from Observable import Observer
from filetypes import Allmusic, Amazon, CdUniverse, Guardian, Laut, Metacritic, MetalObserver, Pitchfork, \
    Plattentests, ProgressiveWorld, RollingStone, Text
from filetypes.legacy import Aversionline, BBC, DrownedInSound, NME, Playlouder, Punkbands, Sputnik, StylusMagazine


class FileProcessor(Observer):
    timeout = 10
    logger = logging.getLogger("FileProcessor")
    extensionlist = [".txt", ".Txt", ".TXT", ".htm", ".Htm", ".HTM", ".html", ".Html", ".HTML", ".php", ".PHP",
                     ".nfo", ".Nfo", ".NFO", "README", "readme", "Readme"]

    def __init__(self, proxyObject, configObject):
        self.amarok = proxyObject
        self.config = configObject
        self.observe(self.config)
        self.status = 0
        self.tmpdir = TMPDIR
        self.bodycode = ' id="body" style="border:0px none; padding:0px 4px; margin:0px;"'
        self.iframescript = file(os.path.join(os.path.dirname(__file__), "iframe.js")).read()

        self.css = ''
        self.filenames = list()
        self.originalfilenames = list()
        self.currentalbum = ''
        self.manualsearchsite = ''

        self.sites = {
            'allmusic.com': Allmusic.config,
            'amazon.com': Amazon.config,
            'cduniverse.com': CdUniverse.config,
            'guardian.co.uk': Guardian.config,
            'laut.de': Laut.config,
            'metacritic.com': Metacritic.config,
            'metal-observer.com': MetalObserver.config,
            'pitchfork.com': Pitchfork.config,
            'plattentests.de': Plattentests.config,
            'progressiveworld.net': ProgressiveWorld.config,
            'rollingstone.com': RollingStone.config
        }

        # =======================================================================
        # IF YOU WANT TO ADD A SITE - see the examples in directory 'filetypes'
        # =======================================================================
        #
        # if available, use the site's own search, required config keys are:
        # - base: the base url
        # - search: the relative url for a search with %s for the artist name
        # - link: a regexp with a group matching the relative url for a hit with %s for the album name
        #
        # optional keys:
        # - artistlink: (if there are separate artist pages) a regexp with a group matching
        #               the relative url for a hit with %s for the artist name
        # - albumlink
        # - post
        # - search_with_album, search_space_char
        # - extra_check, eliminate, append2link
        #
        # or use google, required keys are:
        # - google
        #
        # optional:
        # - extra_term, search_with_dash, extra_check
        # - inurl, intitle, intitle2 have been removed because it makes google think we are evil

        #
        # then:
        # - add a case in processFile()
        # - do some testing
        # - send me the patch!
        #

        try:
            os.mkdir(self.tmpdir)
        except OSError, e:
            if e.errno is 17:  # already exists
                pass
            else:
                popup("Amarok Reader can not create directory " + self.tmpdir + "\n"
                      "Please check you have write permissions there.")
                self.status = 1

    def setCSS(self, css):
        self.css = "<style>" + css + "</style>"

    def reInit(self):
        self.cleanup()
        self.filenames = list()
        self.originalfilenames = list()
        # self.filetexts = list()
        # self.currentfilename = self.config["fileName"]
        self.songdir = ""

    def findFiles(self, songfilename):
        self.reInit()
        self.songdir = unicode(os.path.dirname(songfilename), 'utf-8')
        try:
            songdirfiles = os.listdir(self.songdir)
            songdirfiles.sort()
        except Exception as e:
            self.logger.error("%s", e)
            return

        for f in songdirfiles:
            for ext in self.extensionlist:
                if f.endswith(ext):
                    self.processFile(os.path.join(self.songdir, f))
                    self.logger.debug("found file %s", f)

        if len(self.filenames) is 0:
            # self.amarok.contextBrowser.showMessage("Amarok Reader did not find any text files.")
            self.logger.debug("no files")

        return len(self.filenames)

    def manualSearch(self, sitename):
        self.manualsearchsite = sitename

    def initSearchSites(self, autoSearchSites):
        s = autoSearchSites.split(" ")
        for siteconf in s:
            sitename, enabled = siteconf.split(":")
            if not sitename in self.sites: continue
            if enabled == "True":
                self.sites[sitename]["enabled"] = True
            else:
                self.sites[sitename]["enabled"] = False

        for sitename, site in self.sites.items():
            if not 'enabled' in site:
                site["enabled"] = False
                autoSearchSites += " " + sitename + ":False"

        autoSearchSites = autoSearchSites.strip()
        s = autoSearchSites.split(" ")
        s.sort()
        return string.join(s)

    def findOnlineReviews(self, artist, album):

        def get(url):
            self.logger.debug("get %s", url)
            url = re.sub("http://", "", url)
            host, url = url.split('/', 1)

            h = httplib.HTTPConnection(host)
            h.timeout = self.timeout
            h.putrequest('GET', "/" + url)
            h.putheader('Connection', 'close')
            h.putheader('Accept', '*/*')
            h.putheader('Referer', 'http://www.google.com/webhp?hl=en')
            h.endheaders()
            h.sock.settimeout(self.timeout)

            response = h.getresponse()
            self.logger.debug("%s, %s", response.status, response.reason)
            if response.status == 302 or response.status == 301:
                return get(response.getheader("Location"))

            data = response.read()
            #self.logger.debug("%s", data)
            return data

        def post(url, params):
            self.logger.debug("post %s", url)
            url = re.sub("http://", "", url)
            host, url = url.split('/', 1)

            headers = {"Content-type": "application/x-www-form-urlencoded",
                       "Accept": "text/html"}
            h = httplib.HTTPConnection(host)
            h.timeout = self.timeout
            h.request('POST', "/" + url, params, headers)
            #h.putheader('Connection', 'close')
            #h.putheader('Accept', '*/*')
            #h.endheaders()
            h.sock.settimeout(self.timeout)

            response = h.getresponse()
            self.logger.debug("%s, %s", response.status, response.reason)
            if response.status == 302 or response.status == 301:
                return post(response.getheader("Location"), params)

            data = response.read()
            #self.logger.debug("%s", data)
            return data

        def mustHide(site):
            for domain in self.getHideDomains().split():
                if site.endswith(domain):
                    return True
            return False

        if self.currentalbum == album and self.config["saveOnlineReviews"] and not self.manualsearchsite:
            return -1

        self.currentalbum = album
        misses = list()
        hits = 0
        for sitename, site in self.sites.items():
            self.logger.debug(">>> %s", sitename + "+++" + self.manualsearchsite)
            if self.manualsearchsite:
                if sitename != self.manualsearchsite:
                    continue
            else:
                if not site['enabled'] or mustHide(sitename):
                    continue

            try:
                self.amarok.contextBrowser.evalJS('info(-1)')

                if 'google' in site and site['google'] is True:
                    # ----------
                    # use google site: search

                    # if 'intitle' in site:
                    #     if site['intitle'] == ALBUM:
                    #         intitle = '+intitle:"' + urllib.quote(album) + '"'
                    #     elif site['intitle'] == ARTIST:
                    #         intitle = '+intitle:"' + urllib.quote(artist) + '"'
                    #     else:
                    #         intitle = '+"' + urllib.quote(site['intitle']) + '"'
                    #     if 'intitle2' in site:
                    #         intitle += '+intitle:"' + urllib.quote(site['intitle2'] + '"')
                    # else:
                    #     intitle = ""

                    if 'search_with_dash' in site:
                        searchstr = '"' + artist + ' - ' + album + '"'
                    else:
                        searchstr = '"' + artist + '"+"' + album + '"'

                    if 'extra_term' in site:
                        searchstr += '+' + site['extra_term']

                    data = get("www.google.com/search?hl=en&source=hp&q=%s+site:%s+%s%s&btnI=%s&aq=f&oq=&aqi=" % (
                        urllib.quote(searchstr),
                        urllib.quote(sitename),
                        '',  # urllib.quote(site['inurl']),
                        '',  # intitle,
                        urllib.quote("I'm Feeling Lucky")
                    ))

                    if 'extra_check' in site:
                        if not re.search(site['extra_check'], data, re.S):
                            misses.append(sitename)
                            self.logger.debug('\'extra_check\' failed')
                            self.amarok.contextBrowser.evalJS('searchFailure("' + sitename + '")')
                            continue

                    # self.logger.debug(data)

                    if 'did not match any documents' in data:
                        misses.append(sitename)
                        self.amarok.contextBrowser.evalJS('searchFailure("' + sitename + '")')
                        continue
                    if 'We apologize for the inconvenience' in data:
                        misses.append(sitename + " (!)")
                        self.amarok.contextBrowser.evalJS('searchFailure("' + sitename + '")')
                        continue
                    if 'Our systems have detected unusual traffic' in data:
                        misses.append(sitename + " (!)")
                        self.amarok.contextBrowser.evalJS('searchFailure("' + sitename + '")')
                        continue

                else:
                    # ---------------------
                    # use the site's search

                    if 'search_with_album' in site:
                        searchterm = urllib.quote(artist + " " + album)
                    else:
                        searchterm = urllib.quote(artist)

                    if 'search_space_char' in site:
                        searchterm = re.sub('%20', site['search_space_char'], searchterm)

                    if 'post' in site:
                        data = post(site['base'] + site['search'], site['post'] % artist)
                    else:
                        data = get(site['base'] + site['search'] % searchterm)

                    if 'eliminate' in site:
                        for item in site['eliminate']:
                            data = re.sub(item, '', data)
                            #self.logger.debug(data)

                    if 'album_maxchars' in site:
                        matchalbum = album[:site["album_maxchars"]] + '(?:...)?'
                    else:
                        matchalbum = album

                    if 'artistlink' in site:
                        # find artist link
                        r = re.search(site['artistlink'] % artist, data, re.S | re.I)
                        if r:
                            link = r.group(1)
                            if link[:1] != '/': link = '/' + link
                            link = re.sub('&amp;', '&', link)
                            self.logger.debug('artistlink: ' + link)
                            data = get(site['base'] + link)

                    if 'albumlink' in site:
                        # find album link
                        r = re.search(site['albumlink'] % matchalbum, data, re.S | re.I)
                        if r:
                            link = r.group(1)
                            if link[:1] != '/': link = '/' + link
                            link = re.sub('&amp;', '&', link)
                            self.logger.debug(link)
                            data = get(site['base'] + link)
                            r = re.search(site['link'], data, re.S | re.I)
                    else:
                        # find review link:
                        r = re.search(site['link'] % matchalbum, data, re.S | re.I)

                    if r:
                        link = r.group(1)
                        if link[:1] != '/':
                            link = '/' + link
                        if 'append2link' in site:
                            link += site['append2link']
                        link = re.sub('&amp;', '&', link)
                        self.logger.debug(link)
                        data = get(site['base'] + link)
                    else:
                        misses.append(sitename)
                        self.logger.debug('\'link\' not found')
                        self.amarok.contextBrowser.evalJS('searchFailure("' + sitename + '")')
                        continue

                if 'extra_check' in site:
                    if not re.search(site['extra_check'], data, re.S):
                        misses.append(sitename)
                        self.logger.debug('\'extra_check\' failed')
                        self.amarok.contextBrowser.evalJS('searchFailure("' + sitename + '")')
                        continue

            except Exception, e:
                self.logger.debug(e)
                self.amarok.contextBrowser.showMessage("Amarok Reader could not connect to <b>%s</b>!" % sitename)
                self.amarok.contextBrowser.evalJS('searchError("' + sitename + '","no connection")')
                #self.manualsearchsite = ''
                #return -1
                continue

            hits += 1
            self.amarok.contextBrowser.evalJS('searchSuccess("' + sitename + '")')

            title = sitename
            if self.config["saveOnlineReviews"] and self.songdir:
                filename = os.path.join(self.songdir, title + ".html")
            else:
                filename = os.path.join(os.path.abspath(self.tmpdir), title + ".html.html")

            def writeFile():
                self.logger.debug("trying to write %s", filename)
                f = open(filename, 'w')
                f.write(data)
                f.close()

            try:
                writeFile()
            except:
                # no write permission - use tmp path
                self.logger.error("could not write file %s", filename)
                filename = os.path.join(os.path.abspath(self.tmpdir), title + ".html.html")
                self.logger.error("trying %s", filename)
                writeFile()

            self.processFile(filename)

        if len(misses) > 0:
            self.amarok.contextBrowser.showMessage(
                "Amarok Reader could not find a review for <b>%s</b> on %s" % (album, string.join(misses, ', ')))

        self.manualsearchsite = ''
        return hits

    def processFile(self, filename):
        #filename = unicode(filename)
        f = open(filename, 'r')
        text = f.read()
        f.close()

        if False:
            pass

        # known review files
        elif Allmusic.matches(text):
            f = Allmusic.AllmusicFile(text)
            self.sites['allmusic.com']['enabled'] = False

        elif Amazon.matches(text):
            f = Amazon.AmazonFile(text)
            self.sites['amazon.com']['enabled'] = False

        elif Aversionline.matches(text):
            f = Aversionline.AversionlineFile(text)

        elif BBC.matches(text):
            f = BBC.BBCFile(text)

        elif CdUniverse.matches(text):
            f = CdUniverse.CdUniverseFile(text)
            self.sites['cduniverse.com']['enabled'] = False

        elif DrownedInSound.matches(text):
            f = DrownedInSound.DrownedInSoundFile(text)

        elif Guardian.matches(text):
            f = Guardian.GuardianFile(text)
            self.sites['guardian.co.uk']['enabled'] = False

        elif Laut.matches(text):
            f = Laut.LautFile(text)
            self.sites['laut.de']['enabled'] = False

        elif Metacritic.matches(text):
            if Metacritic.matches(text) == 1:
                f = Metacritic.MetacriticFile(text)
            elif Metacritic.matches(text) == 2:
                f = Metacritic.MetacriticFile_v2(text)
            self.sites['metacritic.com']['enabled'] = False

        elif MetalObserver.matches(text):
            f = MetalObserver.MetalObserverFile(text)
            self.sites['metal-observer.com']['enabled'] = False

        elif NME.matches(text):
            f = NME.NMEFile(text)

        elif Pitchfork.matches(text):
            f = Pitchfork.PitchforkFile(text)
            self.sites['pitchfork.com']['enabled'] = False

        elif Plattentests.matches(text):
            f = Plattentests.PlattentestsFile(text)
            self.sites['plattentests.de']['enabled'] = False

        elif Playlouder.matches(text):
            f = Playlouder.PlaylouderFile(text)

        elif ProgressiveWorld.matches(text):
            f = ProgressiveWorld.ProgressiveWorldFile(text)
            self.sites['progressiveworld.net']['enabled'] = False

        elif Punkbands.matches(text):
            f = Punkbands.PunkbandsFile(text)

        elif RollingStone.matches(text):
            f = RollingStone.RollingStoneFile(text)
            self.sites['rollingstone.com']['enabled'] = False

        elif StylusMagazine.matches(text):
            f = StylusMagazine.StylusMagazineFile(text)

        elif Sputnik.matches(text):
            f = Sputnik.SputnikFile(text)

        # html file
        elif (filename.endswith(".htm") or
              filename.endswith(".HTM") or
              filename.endswith(".html") or
              filename.endswith(".HTML") or
              '<html>' in text or '<HTML>' in text):
            f = Text.HTMLFile(text)

        # NFO file
        elif (filename.endswith(".nfo") or
              filename.endswith(".NFO")):
            f = Text.NFOFile(text)

        else:
            f = Text.TextFile(text)
            f.wrap()

        if filename.endswith(".html.html"):
            filename = filename[:-5]

        self.writeTmpFile(f, filename)

    def writeTmpFile(self, f, filename):
        def regexEscape(s):
            # if not re.match("javascript", s):
            #     s = re.sub('\(', '\\(', s)
            #     s = re.sub('\)', '\\)', s)
            s = re.sub('\?', '\\?', s)
            s = re.sub('\+', '\\+', s)
            s = re.sub('\|', '\\|', s)
            s = re.sub('\*', '\\*', s)
            s = re.sub('\(', '\\(', s)
            s = re.sub('\)', '\\)', s)
            s = re.sub('\{', '\\{', s)
            s = re.sub('\}', '\\}', s)
            s = re.sub('\[', '\\[', s)
            s = re.sub('\]', '\\]', s)
            s = re.sub('\^', '\\^', s)
            s = re.sub('\$', '\\$', s)
            return s

        head = self.css + f.css
        # self.logger.debug("currentfilename = %s", self.currentfilename)
        self.logger.debug("currentalbum = %s", self.currentalbum)

        # replace links so that clicks become "pollable"
        # if self.config["externalBrowser"]:
        f.text = re.sub('javascript: ', 'javascript:', f.text)
        links = re.findall('(?i)<a[^>]* href=["\']?([^"\'> ]*)["\']?[^>]*>', f.text)
        for link in links:
            full_link = link
            if not (link.startswith("http") or link.startswith("mailto")):
                if link.startswith("/"):
                    full_link = link[1:]
                full_link = 'basehref()+' + '\'%s\'' % full_link
            else:
                full_link = '\'%s\'' % link

            link = regexEscape(link)
            # self.logger.debug(link)

            try:
                f.text = re.sub('(?i)<a[^>]* href=["\']?%s["\']?' % link,
                                '<a href="javascript:parent.openURL(%s)"' % full_link, f.text)
            except Exception:
                # links will not work, no need to fail completely
                pass


        writetext = '<html><head>' + head + '</head>' + \
                    '<body' + self.bodycode + '>' + f.text + \
                    '<script>' + self.iframescript + '</script>' + \
                    '</body></html>'

        # need abspath for the iframe later
        tmpfilename = os.path.join(os.path.abspath(self.tmpdir), os.path.basename(filename)) + '.html'
        try:
            self.logger.debug("trying to write %s", tmpfilename)
            tmpfile = open(tmpfilename, 'w')
            tmpfile.write(writetext)
            tmpfile.close()
            self.status = 0
        except IOError, e:
            if self.status is 0:
                popup("Amarok Reader can not write to directory " + os.path.abspath(self.tmpdir))
                self.status = 1
            self.logger.error("writing tmp file failed: %s", e)

        if f.injectable:
            # self.filetexts.append(f.unmodifiedtext)
            self.filenames.append(tmpfilename)
            self.originalfilenames.append(filename)
        else:
            if self.status is 0:
                # self.filetexts.append("")
                self.filenames.append(tmpfilename)
                self.originalfilenames.append(filename)

    # def fileText(self, index):
    #     return self.filetexts[index]

    def fileName(self, index):
        return self.filenames[index]

    def originalFileName(self, index):
        return self.originalfilenames[index]

    def numFiles(self):
        return len(self.filenames)

    def getInitialSites(self):
        s = ""
        for sitename, site in self.sites.items():
            s = s + sitename + ":False "
        return s.rstrip()

    def getHideDomains(self):
        hideDomains = ""
        if self.config["hideDotCom"]:
            hideDomains += '.com '
        if self.config["hideDotCoUk"]:
            hideDomains += '.uk '
        if self.config["hideDotDe"]:
            hideDomains += '.de '
        if self.config["hideDotNet"]:
            hideDomains += '.net '
        return hideDomains.rstrip()

    def cleanup(self):
        for f in self.filenames:
            try:
                os.remove(f)
                self.logger.debug("Removed temp file " + f)
            except OSError, e:
                self.logger.debug(str(e.errno) + ": Could not remove temp file " + f)
                pass
