import re
from Text import TextFile

config = {
    'base': "http://www.metal-observer.com",
    'search': "/search.php?q=%s&sa.x=0&sa.y=0",
    'link': '<A href="http://www.metal-observer.com(/articles.php\?lid=1&sid=1&id=[0-9]*)"><STRONG>%s'
}


def matches(text):
    return '<TITLE>THE METAL OBSERVER' in text


class MetalObserverFile(TextFile):
    def __init__(self, text):
        self.log("init")
        tmptext = ""
        s = re.search(
            '(<TABLE border="0" cellpadding="0" cellspacing="0" width="100%"><TR>.*?)<script type="text/javascript">',
            text, re.S) # title and data
        if s: tmptext += s.group(1)
        s = re.search('(<TR height=150>.*?</TR>)', text, re.S) # tool box
        if s: tmptext += s.group(1)

        tmptext = re.sub('COLOR: silver;|FONT-SIZE: 10pt|FONT-FAMILY: Arial;', '', tmptext)
        tmptext = re.sub('COLOR: #.{6}|LINE-HEIGHT: [0-9]*(%|em|px|pt)|FONT-FAMILY: [\'",-A-Za-z]*', '', tmptext)
        tmptext = re.sub('<FONT.*?>', '', tmptext)

        tmptext += """<script>
            function printArticle(lid, sid, id) {
                parent.openURL('http://www.metal-observer.com/articles_print.php?lid=' + lid + '&sid=' + sid + '&id=' + id);
            }
            </script>"""

        self.text = '<div id="wiki_box-body" class="box-body">' + tmptext + '</div>'

        self.css += """
            <base href="http://www.metal-observer.com/">
            <style type="text/css">
                /*body, p, td, div, font,span { font-size:50%; }*/
            </style>
            """

