import re
from ..Text import TextFile

# self.sites['punkbands.com'] = {}
# self.sites['punkbands.com']['base'] = "punkbands.com"
# self.sites['punkbands.com']['search'] = "/bands/search"
# self.sites['punkbands.com']['artistlink'] = '(/bands/[^"]*)">%s</a>'
# self.sites['punkbands.com']['albumlink'] = '(/albums/[^"]*)">%s</a>'
# self.sites['punkbands.com']['link'] = '(/reviews/[^"]*)">read full review'
# self.sites['punkbands.com']['post'] = 'q=%s&a=search'


def matches(text):
    return '<title>punkbands.com' in text or \
           'Punkbands dot com</title>' in text


class PunkbandsFile(TextFile):
    def __init__(self, text):
        self.log("init")
        tmptext = ""

        #old
        s = re.search('class="type3">(.*?)<form', text, re.S)  # title and data
        if s: tmptext += s.group(1)

        s = re.search('(<h2.*?)<div class="side">', text, re.S)
        if s: tmptext += s.group(1)

        tmptext = re.sub('href="javascript:;', '', tmptext)
        tmptext = re.sub('"images/ratings/(.).gif"', '"images/ratings/\\1.gif" width="40" alt="\\1 stars"', tmptext)

        tmptext = re.sub('<img src="/_images/sub/reviews/ratings/large/[0-9]*.gif" alt="(.*?)" />', '<b>\\1</b>', tmptext)
        tmptext = re.sub('<img src="images/ratings/[0-9]*.gif".*?alt="(.*?)">', '<b>\\1</b>', tmptext)

        self.text = '<div id="wiki_box-body" class="box-body">' + tmptext + '</div>'

        self.css += """
            <base href="http://www.punkbands.com/">
            <style type="text/css">
                /*.newspostedby, .newstext, .newscomments, .newstitle, h2, h3 { font-size:50%; }*/
                .user { display:block; font-weight:bold; }
            </style>
            """


