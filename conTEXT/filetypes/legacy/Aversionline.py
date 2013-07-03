import re
from ..Text import TextFile


def matches(text):
    return 'AVERSIONLINE.COM</title>' in text


class AversionlineFile(TextFile):
    def __init__(self, text):
        self.log("init")
        tmptext = ""
        s = re.search('<!-- content START -->(.*?)<!-- content END -->', text, re.S)  # text
        if s: tmptext += s.group(1)

        self.text = '<div id="wiki_box-body" class="box-body">' + tmptext + '</div>'

        self.css += """
            <base href="http://www.aversionline.com/">
            <style type="text/css">
                /*body, td { font-size:50%; }*/
            </style>
            """
