import re
from ..Text import TextFile

#self.sites['bbc.co.uk'] = {}
#self.sites['bbc.co.uk']['base'] = "http://www.bbc.co.uk"
#self.sites['bbc.co.uk']['search'] = "/cgi-bin/search/results.pl?q=%s&uri=/music/release/&go.x=0&go.y=0"
#self.sites['bbc.co.uk']['search_with_album'] = True
#self.sites['bbc.co.uk']['eliminate'] = ['<b>', '</b>', '<em class="searchterm">', '</em>']
#self.sites['bbc.co.uk']['link'] = '%s by.*?<p class="displayUrl">www.bbc.co.uk(/music/reviews/[^<]*)</p>'


def matches(text):
    return '<title>BBC' in text


class BBCFile(TextFile):
    def __init__(self, text):
        self.log("init")
        tmptext = ""

        s = re.findall('(<style type="text/css".*?/style>)', text)  # css
        for s in s:
            tmptext += s

        # ver.1
        s = re.search('((?:<!-- )?<td valign="top" class="reviewtitle">.*?<tr><td>)<a name="comment">', text,
                      re.S)  # title and data
        if s:
            tmptext += s.group(1)
        else:
            # ver.3
            s = re.search('(<h3>Review</h3>.*?)<div id="nav">', text, re.S)  # title and data
            if s:
                tmptext += s.group(1)
                s = re.search('(<h3>Key Tracks</h3>.*?)<!-- begin IPS', text, re.S)
                if s:
                    tmptext += s.group(1)
            else:
                # ver.2
                s = re.search('<!-- End of GLOBAL NAVIGATION  -->(.*?)<div id="nav">', text, re.S)  # title and data
                if s:
                    tmptext += s.group(1)
                else:
                    s = re.search('(<div id="summary".*?)<span class="mb_font"', text, re.S)
                    if s:
                        tmptext += s.group(1)
                    s = re.search('(<div id="main_content">.*?)<a name="postcomment">', text, re.S)
                    if s:
                        tmptext += s.group(1)
                    tmptext = re.sub('class="box">', '>', tmptext)

        # add comment link at bottom
        s = re.search('name="uri" value="([^"]*)"', text)  # page uri
        if s:
            uri = s.group(1)
            tmptext = re.sub('a href="#comment"', 'a href="' + uri + '#comment"', tmptext)
            tmptext += 'Have you heard this album? <a href="' + uri + '#comment">Tell us what you think</a>'

        # remove comment form (doesnt work)
        tmptext = re.sub('(?s)<a name="comment">.*?</form>.*?</div>', '<h4>Comments</h4>', tmptext)
        # remove misc stuff
        #tmptext = re.sub('<h1>.*?</h1>', '', tmptext)
        tmptext = re.sub('<(dt)/?>', '&nbsp;&nbsp;', tmptext)
        tmptext = re.sub('<(dd)/?>', '', tmptext)
        tmptext = re.sub('<img alt="Picture of:.*?>', '', tmptext)

        self.text = '<div id="wiki_box-body" class="box-body">' + tmptext + '</div>'

        # self.css = """
        #     <base href="http://www.bbc.co.uk/">
        #     <style type="text/css">
        #         /*body, p, td, div, font, h1,h2,h3,h4,h5,h6 { font-size:50%; }*/
        #         .acs_name { font-weight:bold; }
        #     </style>
        #     """