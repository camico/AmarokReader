import re
from ..Text import TextFile

#self.sites['playlouder.com'] = {}
#self.sites['playlouder.com']['base'] = "http://www.playlouder.com"
#self.sites['playlouder.com']['search'] = "/find/artistsearch.html?searchtext=%s"
#self.sites['playlouder.com']['link'] = '<a href="(/review[^"]*)">%s</a>'


def matches(text):
    return '<title>PLAYLOUDER | review' in text or \
           'PLAYLOUDER</title>' in text


class PlaylouderFile(TextFile):
    def __init__(self, text):
        self.log("init")
        tmptext = ""
        #s = re.findall("(<link type.*?>)", text) # css
        #for s in s: tmptext += s
        s = re.search("(<div class=\"reviewheader\">.*?)<!--", text, re.S)  # title and data
        if s:
            tmptext += s.group(1)

        tmptext = re.sub('<h.*?>', '', tmptext)
        tmptext = re.sub('</h.>', '', tmptext)

        tmptext = re.sub('<img src="/review/images/fullhead.gif".*?>', '<b>*</b>', tmptext, 0, re.S)

        self.text = '<div id="wiki_box-body" class="box-body">' + tmptext + '</div>'

        self.css += """
            <style type="text/css">
            </style>
            <base href="http://www.playlouder.com/">
            """