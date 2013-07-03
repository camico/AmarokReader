import re
from Text import TextFile

config = {
    'google': True,
    'extra_check': 'itemprop="reviewBody"'
}


def matches(text):
    return '<title>Guardian Unlimited Arts' in text or \
           'Guardian Unlimited Arts</title>' in text or \
           '<div id="guardian-logo"' in text


class GuardianFile(TextFile):
    def __init__(self, text):
        self.log("init")
        tmptext = ""
        s = re.search('(<div id="(GuardianArticle|main-article-info)">.*?)(<br id="articleend">|<div id="related">)',
                      text, re.S)  # title and data
        if s: tmptext += s.group(1)

        tmptext = re.sub('height="250"', 'height="0"', tmptext)
        tmptext = re.sub('Article continues', '', tmptext)
        tmptext = re.sub('(?s)</h1>.*?<BR>.*?<BR>', '</h1>', tmptext)
        tmptext = re.sub('(?i)<font.*?>|</font>', '', tmptext)
        tmptext = re.sub('<BR>\s*<BR>', '<br>', tmptext)
        tmptext = re.sub('(?i)<HR.*?>', '', tmptext)
        tmptext = re.sub('(?i)<B>(.*?The Guardian</a>)</B>', '\\1<br>', tmptext)

        self.text = '<div id="wiki_box-body" class="box-body">' + tmptext + '</div>'

        self.css += """
            <base href="http://www.guardian.co.uk/">
            <meta http-equiv="Content-Type" content="text/html; charset=utf8">
            <style type="text/css">
                /*body, p, td, div, font, h1,h2,h3,h4 { font-size:50%; }*/
                .image, .inline, .contributor-pic-small {display:none;}
                .rating-container { background-color: red; width:68px;}
                ul {list-style-type:none;}
                .tweet_button, .facebook, .reddit, .buzz, .twitter-share-button, .email, .amazon-header,
                    .comment-count, .fact-list, .picture
                    { display:none }
                h1, #stand-first { margin:0; padding: 0 }
                ol.affiliated { list-style-type: none }
            </style>
            """

