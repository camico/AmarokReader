import re
from Text import TextFile

config = {
    'base': "http://www.cduniverse.com",
    'search': "/sresult.asp?HT_Search_Info=%s&HT_Search=ARTIST&style=music",
    'link': '(/productinfo.asp[^"]*)"><font size="2"><b>%s',
    'append2link': '&fulldesc=T'
    # 'extra_check': 'iheadmess">(CD Notes|Review)|<!---- trimable --->[^<]'
}


def matches(text):
    return 'content="Music, Movies and Games Shopping at CD Universe"' in text \
        or 'https://www.cduniverse.com/checkout/' in text


class CdUniverseFile(TextFile):

    def __init__(self, text):
        self.log("init")
        tmptext = ""
        s = re.search("<title>(.*?) CD", text)
        if s:
            tmptext += "<b>" + s.group(1) + "</b><p>"

        tmptext = self.description(text, tmptext)
        tmptext = self.notes(text, tmptext)
        tmptext = self.customerreviews(text, tmptext)

        tmptext = re.sub('(CD )?Notes', '<b>Notes</b>', tmptext)
        tmptext = re.sub('Customer Reviews', '<br><b>Customer Reviews</b>', tmptext)
        tmptext = re.sub('<br>Was This Review Helpful.*?No</a>', '', tmptext)
        tmptext = re.sub('Customer (.*?) Reviews', '<br><b>Customer Reviews</b>', tmptext)
        tmptext = re.sub('Review</span>', 'Review ', tmptext)
        tmptext = re.sub('Review[^s]', '<br><b>Review</b>', tmptext)
        tmptext = re.sub(' align="?justify"?', '', tmptext)

        tmptext += "<script>" \
                   "document.getElementById('NoteSnippet').style.display='inline'; " \
                   "document.getElementById('NoteSnippet').style.visibility='visible';" \
                   "</script>"

        self.text = '<div id="wiki_box-body" class="box-body">' + tmptext + '</div>'

        self.css += """
            <base href="http://www.cduniverse.com/">
            <style type="text/css">
                .notimportantlink  {display:none}
            </style>
            """

    def description(self, text, tmptext):
        s = re.search('arrown.gif"> (Review.*?<div align="?justify"?>.*?</div>)', text, re.S)  # v1
        if s: tmptext += s.group(1)

        s = re.search('<!---- trimable --->(.*?)<!---- trimable --->', text, re.S)  # v2
        if s: tmptext += s.group(1)

        s = re.search('(<span itemprop="description">.*?</span>)', text, re.S)  # v3
        if s: tmptext += s.group(1)

        return tmptext

    def notes(self, text, tmptext):
        s = re.search('arrown.gif"> (Notes.*?<div align="?justify"?>.*?</div>)', text, re.S)  # v1
        if s: tmptext += s.group(1)

        s = re.search('iheadmess">(CD Notes.*?<div align="?justify"?>.*?</div>)', text, re.S)  # v2
        if s: tmptext += s.group(1)

        s = re.search('(<table style="margin-top:10px;" id="PDTable">.*?</table>)', text, re.S)  # v3
        if s: tmptext += s.group(1)

        return tmptext

    def customerreviews(self, text, tmptext):
        s = re.search('arrown.gif"> (Customer Reviews.*?<div align="?justify"?>.*?</div>)', text, re.S)  # v1
        if s: tmptext += s.group(1)

        s = re.search('arrown.gif"> (Customer  <span class="iheadmess">.*?<div align="?justify"?>.*?</div>)', text, re.S)  # v2
        if s: tmptext += s.group(1)

        s = re.search('(<div id="reviewwrapper">.*?)<table border="0" cellspacing="0"', text, re.S)  # v3
        if s:
            tmptext += "<p>" + s.group(1)
            tmptext = re.sub('album for sale|CD music', '', tmptext)

        return tmptext
