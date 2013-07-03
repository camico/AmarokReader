import re
from Text import TextFile

config = {
    'base': "http://www.allmusic.com",
    'search': "/search/artists/%s",
    'search_space_char': '-',
    'artistlink': '(/artist/[^"]*)"[^>]*>%s( \[.*?\])?</a>',
    'link': '(/album/[^"]*)" class="title[^>]*>%s( \[.*?\])?</a>'
}


def matches(text):
    return '<TITLE>allmusic' in text or 'AllMusic</title>' in text


class AllmusicFile(TextFile):

    def __init__(self, text):
        self.log("init")
        tmptext = ""

        tmptext = self.rating(text, tmptext)
        tmptext = self.review(text, tmptext)
        tmptext = self.genres(text, tmptext)
        tmptext = self.moods(text, tmptext)
        tmptext = self.tracks(text, tmptext)

        #v1
        tmptext = re.sub('<img src="/i/pages/site/icons/speaker.gif".*?>', '', tmptext)
        tmptext = re.sub('<img src="/i/pages/site/icons/check.gif" alt="AMG Pick.*?>', '*&nbsp;', tmptext)
        tmptext = re.sub('<img src="/i/pages/site/icons/mini-amg.gif".*?/>', '&nbsp;', tmptext)

        tmptext = re.sub('width="582"', '', tmptext)
        tmptext = re.sub('padding-bottom:5px', '', tmptext)  # listings
        tmptext = re.sub('padding-bottom:4px', 'padding:3px', tmptext)  # review text
        tmptext = re.sub('<img src="/i/pages/site/blocks.*?>', '', tmptext)
        tmptext = re.sub('<img src="/i/spacer.*?>', '', tmptext)
        tmptext = re.sub('</a></li>', '</a> </li>', tmptext)

        self.text = '<div id="wiki_box-body" class="box-body">' + tmptext + '</div>'

        self.css += """
            <base href="http://www.allmusic.com/">
            <meta http-equiv="Content-Type" content="text/html; charset=utf8">
            <style type="text/css">
                /*body, p, td, font, span, div, h2, th { font-size:50%; font-weight:normal; }*/
                li { display:inline; margin-left:1px; }
                .title { padding:0px; }
                h3 { display:none; }
                .author { float:right; margin: 0; margin-top: -15px; padding: 0; font-size: 85%; font-style: italic;}

                dt, h2, h4 { font-weight: bold; }
                dd ul { margin-left:-40px; }
                table.list td.pick {
                    background: url("http://www.allmusic.com/assets/images/allmusic-pick-small.png") no-repeat transparent;
                    min-width: 20px;
                }
            </style>
            """

    def rating(self, text, tmptext):
        s = re.search('(<img src="[^"]*" alt="([0-9\.]* Stars).*?>)', text, re.S)
        if s:
            tmptext += '<div>Rating</div>'
            tmptext += s.group(2) + '<br>'
        else:
            #v2
            #          e.g. <img src="/img/pages/site/stars/st_r7.gif" alt="star_rating(7)" title="star_rating(7)"/>
            s = re.search('<img.*?alt="star_rating\(([0-9]*)\).*?>', text, re.S)
            if s:
                tmptext += '<div>Rating</div>'
                tmptext += s.group(1) + '/10 <br>'
            else:
                #v3
                s = re.search('itemprop="rating">(.*?)</span>', text, re.S)
                if s:
                    tmptext += '<dt>rating</dt>'
                    tmptext += s.group(1) + '/5 <br>'
        return tmptext

    def review(self, text, tmptext):
        s = re.search('<!--Begin Center Content-->(.*?</p></td></tr></table></div>)', text, re.S)  # text
        if s:
            tmptext += s.group(1) + '<br>'
        else:
            #v2
            s = re.search('<p class="text">(.*?)<div id="tracks">', text, re.S)  # text
            if s:
                s2 = re.search('(<p class="author">.*?</p>)', text, re.S)  # author
                if s2:
                    tmptext += s2.group(1) + '<br style="clear:both">'
                tmptext += s.group(1) + '<br>'
            else:
                #v3
                s = re.search('<div id="review">(.*?)<div class="advertisement', text, re.S)
                if s:
                    tmptext += s.group(1) + '<br>'
        return tmptext

    def genres(self, text, tmptext):
        s = re.search('<!--Begin Genre.*?-->(.*?)<!--End Genre/Styles-->', text, re.S)
        if s:
            # tmptext += '<div>Genre & Styles</div>'
            tmptext += s.group(1)
        else:
            #v3
            s = re.search('(<dt>genre</dt>.*?)<dd class="metaids">', text, re.S)
            if s:
                tmptext += s.group(1)
        return tmptext

    def moods(self, text, tmptext):
        s = re.search('Moods( Listing|/Themes)-->(.*?)<!--End Moods/Themes-->', text, re.S)
        if s:
            # tmptext += '<div>Moods & Themes</div>'
            tmptext += s.group(2)
        else:
            #v3
            s = re.search('(<h4>album moods</h4>.*?)<div class="advertisement', text, re.S)
            if s:
                tmptext += s.group(1)
        return tmptext

    def tracks(self, text, tmptext):
        s = re.search('</p></td></tr></table></div>(.*?)<!--End Center Content-->', text, re.S)
        if s:
            tmptext += s.group(1)
        else:
            #v3
            s = re.search('(<div id="tracks">.*?)<div id="similar-albums"', text, re.S)  # tracks
            if s:
                tmptext += s.group(1)
                tmptext = re.sub('<th class="stream".*?</th>', '', tmptext)
                tmptext = re.sub('<td class="sample pick.*?</td>', '', tmptext)
                # tmptext = re.sub('width="235px"', '', tmptext)
                # tmptext = re.sub('width="237px"', '', tmptext)
                # tmptext = re.sub('width="552px"', '', tmptext)
        return tmptext
