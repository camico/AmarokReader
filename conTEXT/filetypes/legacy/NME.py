import re
from ..Text import TextFile

#self.sites['nme.com'] = {}
#self.sites['nme.com']['base'] = "http://www.nme.com"
#self.sites['nme.com']['search'] = "/index.php?class=search&search_type=site&search_term=%s+reviews&search.x=0&search.y=0"
#self.sites['nme.com']['eliminate'] = ['<b>','</b>','<strong>','</strong>']
#self.sites['nme.com']['link'] = '%s - Album[^"]*"http://www.nme.com(/reviews/[^"]*)"'


def matches(text):
    return '<title>NME.COM - Reviews' in text or \
           'Reviews - NME.COM</title>' in text


class NMEFile(TextFile):
    def __init__(self, text):
        self.log("init")
        tmptext = ""
        text = re.sub('<div style="width: 614px;">', '<div>', text)
        text = re.sub('<img src="/layout/review_rating', '<img style="left:0;" src="/layout/review_rating', text)
        text = re.sub('<img src="/layout/user_rat',
                      '<img style="position:absolute; left:-300px;" src="/layout/user_rat', text)
        text = re.sub('<h3>', '<br><h3>', text)

        s = re.search("(<h2>.*?add your own review</a>)", text, re.S) # title and data
        if s:
            tmptext += s.group(1)
        else:
            s = re.search('(<h1 class="headline".*?</h1>)', text) # headline
            if s: tmptext += s.group(1)
            s = re.search('(<span>[0-9]</span> out of 10)', text) # rating
            if s: tmptext += s.group(1)
            s = re.search('(<p class="sell">.*?)<div id="right_panel">', text, re.S) # text
            if s: tmptext += s.group(1)

        tmptext = re.sub('<li class="comments".*?</li>', '', tmptext)
        tmptext = re.sub('(.+)<br />', '\\1', tmptext)

        self.text = '<div id="wiki_box-body" class="box-body">' + tmptext + '</div>'

        self.css += """
            <style type="text/css">
               /*body, p, td, div, font, h1,h2,h3,h4 { font-size:50%; }*/
            </style>
            <base href="http://www.nme.com/">
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
            """

