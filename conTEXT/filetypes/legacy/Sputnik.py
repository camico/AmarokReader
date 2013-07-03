import re
from ..Text import TextFile


def matches(text):
    return 'sputnikmusic</title>' in text


class SputnikFile(TextFile):
    def __init__(self, text):
        self.log("init")
        tmptext = ""

        s = re.search("<table cellpadding=4 cellspacing=4 width=545>(.*?)<font size=2>Share", text, re.S)
        if s: tmptext += s.group(1)

        self.text = '<div id="wiki_box-body" class="box-body">' + tmptext + '</div>'

        self.css += """
            <base href="http://www.sputnikmusic.com/">
            <style type="text/css">
                /*body, td, h1, h2, h3, div, font { font-size:50%; }*/
            </style>
            """
