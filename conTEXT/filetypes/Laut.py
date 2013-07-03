import re
from Text import TextFile

config = {
    'base': "http://www.laut.de",
    'search': "/Suche?suchbegriff=%s",
    'link': '<a href="(/[^"]*)"><span class="artist">[^>]*>[ ]*<span class="title">%s',
    'extra_check': '<h3 class="klappText">'
}


def matches(text):
    return '<title>laut.de' in text or \
           'window.laut' in text


class LautFile(TextFile):
    def __init__(self, text):
        self.log("init")
        tmptext = ""
        v2 = False
        #s = re.findall('(<style type="text/css".*?/style>)', text) # css
        #for s in s: tmptext += s
        s = re.search('<!-- cover plus info -->(.*?)<div (?:id|class)="spalteKommerz">', text, re.S) # title and data
        if s: tmptext += s.group(1)

        #v2
        s = re.search('<ul class="anzeigeBalken">(.*?)</ul>', text, re.S) # rating
        if s:
            tmptext += s.group(1) + '<br/>'
            v2 = True
        s = re.search('<h3 class="klappText">(.*?)<li class="widget" id="trackliste">', text, re.S)  # title and data
        if s: tmptext += s.group(1)

        tmptext = re.sub('width="292"', 'width="230"', tmptext)
        tmptext = re.sub('margin-top: 37px;', 'margin-top:-20px; float:right;', tmptext)
        tmptext = re.sub('margin-top:12px;', 'margin-top:2px;', tmptext)
        tmptext = re.sub('id="cdInfo"|id="cdInfoButtons"|id="cdInfoText"|id="cdHead"', '', tmptext)
        tmptext = re.sub('leer.gif" height="12"', 'leer.gif" height="0"', tmptext)
        tmptext = re.sub('open\(url,\'leservoting.*', 'location.href=url;', tmptext)
        tmptext = re.sub('<img src="/images/lautstark/lautstark_button_preisvergleich.gif".*?>', '', tmptext)
        tmptext = re.sub('height="(12|6)"', 'height="0"', tmptext)
        tmptext = re.sub('http://s7.addthis.com/js/250/addthis_widget.js#username=lautde', '', tmptext)  # CRASHES AMAROK!
        tmptext = re.sub('weitersagen</a>', '</a>', tmptext)

        s = re.search('<img src="/images/analyse.gif\?USID\&ASID(/lautstark/cd-reviews/.*?)\&', text)
        if s:
            tmptext = re.sub('<a href="http://forum.laut.de/create_topic.php.*?>', '<a href="%s">' % s.group(1),
                             tmptext)

        self.text = '<div id="wiki_box-body" class="box-body">' + tmptext + '</div>'

        if v2:
            self.css += '<meta http-equiv="Content-Type" content="text/html; charset=utf8">'
        else:
            self.css += ''

        self.css += """
            <base href="http://www.laut.de/">
            <style type="text/css">
                .cdCover { display:none; }
                /*body, p, td, div, font, span, h1,h2,h3,h4 { font-size:50%; }*/

                /* v2 */
                #leserWertung { display:inline; }
                li { list-style-type:none; }

            #tracklist
            {
              width: 140px;
              overflow: hidden;
              float: left;
              margin-right: 12px;
              margin-bottom: 4px;
            }
            #tracklist ul
            {
              margin: 0px;
              list-style-type: none;
              padding: 4px 8px 8px 8px;
            }

            #tracklist ul li
            {
              padding: 4px 0px 0px 0px;
            }

            #tracklist ul li img
            {
              margin-left: 0px;
            }

            #tracklist ol
            {
              list-style-position: outside;
              margin: 0px;
              padding: 4px 4px 4px 27px;
            }

            #tracklist ol li
            {
              padding: 2px 0px 2px 0px;
              margin: 0px;
            }

            #tracklist ol li div
            {
              margin-left: -2px;
            }
            </style>
            """
