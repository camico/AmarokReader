import re
from ..Text import TextFile

#self.sites['drownedinsound.com'] = {}
#self.sites['drownedinsound.com']['base'] = "http://www.drownedinsound.com"
#self.sites['drownedinsound.com']['search'] = "/search?q=%s"
#self.sites['drownedinsound.com']['search_with_album'] = True
##self.sites['drownedinsound.com']['artistlink'] = '(/artist/view/[^"]*)">%s</a>'
#self.sites['drownedinsound.com']['eliminate'] = ['<b>','</b>']
#self.sites['drownedinsound.com']['link'] = '(/releases/[0-9]+/reviews/[0-9]+)">.*?%s / Releases'
##self.sites['drownedinsound.com']['extra_check'] = "Our reviews|b_author";


def matches(text):
    return '<title>Drowned in Sound' in text or \
           'Drowned In Sound </title>' in text


class DrownedInSoundFile(TextFile):
    def __init__(self, text):
        self.log("init")
        tmptext = ""
        #s = re.findall("(<link href.*?>)", text) # css
        #for s in s: tmptext += s
        #s = re.findall("(<script src.*?>)", text) # js
        #for s in s: tmptext += s
        s = re.search("(<h3>.*?Post a user review</a></h3>)", text, re.S)  # title and data
        if s:
            tmptext += s.group(1)
        else:
            s = re.search('(<h3>.*?)<div id="footad">', text, re.S)  # title and data
            if s:
                tmptext += s.group(1)
            else:
                s = re.search('(<div class="header".*?)<div id="reply"', text, re.S)  # title and data
                if s:
                    tmptext += s.group(1)
                else:
                    s = re.search('(<div class="content no-border".*?)<div class="panel">', text, re.S)
                    if s:
                        tmptext += s.group(1)
                    s = re.search('(<div class="editorial".*?</ul>)', text, re.S)  # title and data
                    if s:
                        tmptext += s.group(1)
                    s = re.search('(<div class="comments_header".*?)<div class="sign_up', text, re.S)
                    if s:
                        tmptext += s.group(1)

        s = re.search('<a href="(/release/view/[0-9]*)\?type=user">', text)
        if s:
            tmptext = re.sub('<a href="#', '<a href="%s#' % s.group(1), tmptext)

        tmptext = re.sub('(?s)<form.*?/form>', '', tmptext)
        #tmptext = re.sub('(?i)<h..*?>|</h.>', '', tmptext)
        tmptext = re.sub('(?s)<div class="dis_btn">.*?</div>', '', tmptext)
        tmptext = re.sub('<a.*?>\?</a>', '', tmptext)
        tmptext = re.sub('<img.*?src="http://images.drownedinsound.com/resized_images.*?/>', '', tmptext)

        tmptext = re.sub('<img src="/static_images/ratings/([0-9]*).gif".*?>', '<b>\\1/10</b>', tmptext)

        self.text = '<div id="wiki_box-body" class="box-body">' + tmptext + '</div>'

        self.css += """
            <meta http-equiv="Content-Type" content="text/html; charset=utf8">
            <base href="http://www.drownedinsound.com/">
            <style type="text/css">
                /*body, p, td, div, font, h3, h2, h1, h4 { font-size:50%; }*/
                .admin, .artist_tokens, .invisible, .add_comment { display:none; }
                #content img {display:none; }
            </style>
            """