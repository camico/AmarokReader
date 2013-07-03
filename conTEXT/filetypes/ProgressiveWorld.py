import re
from Text import TextFile

config = {
    'google': True,
    'search_with_dash': True,
    'extra_check': '"Back to reviews index"'
}


def matches(text):
    return '<TITLE>PROGRESSIVEWORLD.NET' in text or \
           '<title>ProgressiveWorld.net' in text or \
           '<title>Progressiveworld.net' in text


class ProgressiveWorldFile(TextFile):
    def __init__(self, text):
        self.log("init")
        tmptext = ""

        #v1
        s = re.search('<FONT FACE="Arial">(<STRONG>.*?</UL>\s?</STRONG></FONT></TD></TR>)', text, re.S)
        if s:
            tmptext += s.group(1)

        #v2
        s = re.search('(<font class="title">.*?)\[ <a href="modules\.php\?name=Reviews">Back to Reviews Index', text,
                      re.S)
        if s:
            tmptext += s.group(1)

        tmptext = re.sub('<BLOCKQUOTE/?>', '', tmptext)
        tmptext = re.sub('<center/?>', '', tmptext)
        tmptext = re.sub('<img src="images/reviews/.*?><br>', '', tmptext)

        # add score at top
        s = re.search('(<b>Score:</b>.*?<br>)', text, re.S)
        if s:
            tmptext = re.sub('<b>Year of Release', s.group(1) + '<b>Year of Release', tmptext)

        self.text = '<div id="wiki_box-body" class="box-body">' + tmptext + '</div>'

        self.css += """
            <base href="http://www.progressiveworld.net/html/">
            <style type="text/css">
                /*body, p, td, div, font { font-size:50%; }*/
            </style>
            """

