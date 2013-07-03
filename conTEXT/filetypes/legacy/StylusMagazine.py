import re
from ..Text import TextFile

#self.sites['stylusmagazine.com'] = {}
#self.sites['stylusmagazine.com']['base'] = "http://www.stylusmagazine.com"
#self.sites['stylusmagazine.com']['search'] = "/search.php?search=%s&submit.x=0&submit.y=0"
#self.sites['stylusmagazine.com']['link'] = "<a href='(/reviews/[^']*)'>%s</a>"
#self.sites['stylusmagazine.com']['album_maxchars'] = 32


def matches(text):
    return 'Stylus Magazine</TITLE>' in text


class StylusMagazineFile(TextFile):
    def __init__(self, text):
        self.log("init")
        self.css += """
            <base href="http://www.stylusmagazine.com/">
            <style type="text/css">
                /*body, p, td, div, font { font-size:50%; }*/
            </style>
            """
        #s = re.search("(<LINK REL.*?>)", text) # css
        #if s: self.css += s.group(1)
        s = re.search("(<META HTTP.*?>)", text) # for utf8
        if s: self.css += s.group(1)

        tmptext = ""
        s = re.search("CONTENT -->(.*?)<!-- /CONTENT", text, re.S) # title and data
        if s: tmptext += s.group(1)

        tmptext = re.sub('<div class=\'textbody\'>\s*<BR><BR>', '<div>', tmptext)
        tmptext = re.sub('<br/>\s*<br/>', '<br/>', tmptext)
        tmptext = re.sub('(<P> )?(<img src=\'/images/big_.*?align=left)>', '\\2 height=25>', tmptext)
        tmptext = re.sub('width=100 height=100', 'width=60 height=60 hspace=2 vspace=2', tmptext)
        self.text = '<div id="wiki_box-body" class="box-body">' + tmptext + '</div>'

