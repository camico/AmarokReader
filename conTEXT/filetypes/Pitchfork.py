import re
from Text import TextFile

config = {
    'base': "http://pitchfork.com",
    'search': "/search/?query=%s&filters=album_reviews",
    'link': 'href="(/reviews/albums/[^"]*)">[^>]*>[^>]*>[^>]*>[^>]*>[^>]*>[^>]*>[^>]*>%s'
}


def matches(text):
    return 'Pitchfork Record Review</title>' in text or \
           '<title>Pitchfork' in text or \
           '| Pitchfork\n</title>' in text


class PitchforkFile(TextFile):
    def __init__(self, text):
        self.log("init")
        tmptext = ""

        # title and data
        s = re.search("(<span class=\"reviewtitle.*?)<a", text, re.S)
        if s:
            tmptext += s.group(1)

        s = re.search("(<div class=\"article_body\">.*?</div>)", text, re.S)  # review text
        if s:
            tmptext += s.group(1)
        s = re.search("(<img alt=\"Horizontal-dotbar-2col\".*?)</div>\s*</div>\s*<div id=\"article_column2\"", text,
                      re.S)  # related reviews and news
        if s:
            tmptext += s.group(1)
        else:
            # new
            s = re.search('(<div class="center column">.*?)<div class="right', text, re.S)
            if s:
                tmptext += s.group(1)
            tmptext = re.sub('<img src', '<img width="70" src', tmptext)

        s = re.search('(<div id="main".*?)<div id="side"', text, re.S)
        if s:
            tmptext += s.group(1)

        tmptext = re.sub('(?s)(<a href="http://twitter.com/share".*?</iframe>)', '', tmptext)
        tmptext = re.sub('<img alt="Link-arrow" src="http://assets3.pitchforkmedia.com/images/link-arrow.gif.*?>',
                         '<br>', tmptext)

        self.text = '<div id="wiki_box-body" class="box-body">' + tmptext + '</div>'

        self.css += """
            <meta http-equiv="Content-Type" content="text/html; charset=utf8">
            <style type="text/css">
                /*body, p, a, h1, h2, h3, h4 {font-size:50%;}*/
                img.record_pic {width:100px;}
                img.tombstone-cover-image {width:70px;}
                .share-link {display:none;}

                ul { list-style: none; }
                .artwork img, .youtube { display: none;}

                .review-meta > li .info {
                    margin-left: -30px;
                }
                .review-meta > li {
                    margin: 0px;
                    padding: 0px;
                    position: relative;
                    width: 100%;
                }
                h1,h2,h3,h4 {margin:0}
                .info .outbound {
                    right: 10px;
                    top: 0px;
                    margin: 0px;
                    padding: 0px;
                    position: absolute;
                    width: 40%;
                }
                address {display:inline}
            </style>
            <base href="http://pitchfork.com/">
            """

