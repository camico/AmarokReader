import re
from Text import TextFile

config = {
    'base': "http://www.metacritic.com",
    'search_space_char': '+',
    'search': "/search/all/%s/results",
    'artistlink': '(/person/[^"]*)">%s</a>',
    'link': '(/music/[^"]*)">%s'
}


def matches(text):
    if 'Metacritic.com</title>' in text or 'About Metacritic</A>' in text:
        return 1
    elif 'Metacritic</title>' in text:
        return 2
    else:
        return False


class MetacriticFile(TextFile):
    def __init__(self, text):
        self.log("init")
        tmptext = ""
        #s = re.findall('(<LINK HREF.*?>)', text) # css
        #for s in s: tmptext += s

        #v1
        s = re.search('<H1>(.*?Discuss this album in our forums</A>)', text, re.S) # text
        if s: tmptext += s.group(1)

        #v2
        s = re.search('<h1>(.*?)<!-- end comments -->', text, re.S) # text
        if s: tmptext += s.group(1)

        tmptext = re.sub('PRINT|EMAIL', '', tmptext)
        tmptext = re.sub('User Score:', '', tmptext)
        tmptext = re.sub('<a.*?Read user comments</a><br />', '', tmptext)
        tmptext = re.sub('<a.*?Rate this album &gt;</a>', '', tmptext)
        tmptext = re.sub('<a href="#critics">(.*?)</a>', '\\1', tmptext)
        tmptext = re.sub('<a.*?Read more user comments &gt;</a>', '', tmptext)
        tmptext = re.sub('All critic scores are.*?Learn more...</a>', '', tmptext)
        tmptext = re.sub('How did we calculate this\?', '', tmptext)

        tmptext = re.sub('(?s)<TD WIDTH="150"><IMG.*?</TD>', '<td></td>', tmptext)
        tmptext = re.sub('(?s)<iframe.*?</iframe>', '', tmptext)

        #tmptext = re.sub("(?s)A HREF=\"javascript:;\" onClick=\"window.open\('(.*?)'.*?\">",
        #'a href="\\1;">', tmptext)

        s = re.search('<A HREF="/print(/music/.*?)">', text, re.S)
        if s: tmptext = re.sub('<A HREF="javascript:.*?>', '<A HREF="%s">' % s.group(1), tmptext)

        tmptext = re.sub('<B><A HREF="#critics">Read critic reviews</A></B><BR>', '', tmptext)
        tmptext = re.sub('<B><A HREF="#users">Read user  comments</A></B><BR>', '', tmptext)
        tmptext = re.sub('<IMG SRC="/_images/heads/.*?" ALT="(.*?)".*?>', '\\1', tmptext)
        tmptext = re.sub('<IMG SRC="/_images/scores/outof.*?>', '', tmptext)
        tmptext = re.sub('<IMG SRC="/_images/scores.*?" ALT="(.*?)".*?>', '\\1', tmptext)
        tmptext = re.sub('<TD ALIGN="CENTER" CLASS="(green|yellow|red)">(.*?)</TD>',
                         '<TD><b><span class="\\1">\\2</span></b> out of 10</TD>', tmptext)
        tmptext = re.sub('TD WIDTH="50"', 'TD', tmptext)
        tmptext = re.sub('CELLSPACING="10"', 'CELLSPACING="5"', tmptext)
        tmptext = re.sub('<BR>\s*<SPAN CLASS="subhead">', ' ', tmptext)

        s = re.search('Metascore: ([0-9]*)', tmptext)
        if s:
            score = int(s.group(1))
            if score > 60:
                scoreclass = "green"
            elif score >= 40:
                scoreclass = "yellow"
            else:
                scoreclass = "red"
        else:
            scoreclass = ""

        tmptext = re.sub('Metascore: ([0-9]*)', '<b><span class="%s">\\1</span></b> out of 100' % scoreclass, tmptext)

        tmptext = re.sub('<IMG SRC="/_images/readreview.gif" ALT="(.*?)".*?>', '\\1', tmptext)
        tmptext = re.sub('<IMG SRC="/_images/button_votenow.*?>', '', tmptext)
        tmptext = re.sub("TARGET=\"_blank\"", "", tmptext);

        #v1
        s = re.search('(?s)(<DIV ID="rightlinks">.*?</DIV>)', tmptext)
        if s:
            productlinks = s.group(1)
            tmptext = re.sub('(?s)(<DIV ID="rightlinks">.*?</DIV>)', '', tmptext)
            tmptext += "<hr>" + productlinks

        #v2
        s = re.search('(?s)(<div id="productlinks">.*?</div>)', tmptext)
        if s:
            productlinks = s.group(1)
            tmptext = re.sub('(?s)(<div id="productlinks">.*?</div>)', '', tmptext)
            tmptext += "<hr>" + productlinks

        tmptext = re.sub('<script.*?</script>', '', tmptext)

        self.text = '<div id="wiki_box-body" class="box-body">' + tmptext + '</div>'

        self.css += """
            <meta http-equiv="Content-Type" content="text/html; charset=utf8">
            <base href="http://www.metacritic.com/">
            <style type="text/css">
                /*body, td, h1, h2, h3 { font-size:50%; }*/
                div.greenscorerow {
                    border-left: solid 30px #33CC00;
                    border-bottom: solid 0px #33CC00;
                    padding: 2px 1px;
                    margin-top:10px;
                }
                div.yellowscorerow {
                    border-left: solid 30px #FFFF00;
                    border-bottom: solid 0px #FFFF00;
                    padding: 2px 1px;
                    margin-top:10px;
                }
                div.redscorerow {
                    border-left: solid 30px #FF0000;
                    border-bottom: solid 0px #FF0000;
                    padding: 2px 1px;
                    margin-top:10px;
                }
                div.criticscore {
                    left: -15px;
                    width: 35px;
                    text-align: right;
                    float: left;
                    position: absolute;
                    padding-top: 4px;
                    font-weight:bold;
                }
                .green, .greencell {
                    font-weight: bold;
                    color: #000000;
                    background-color: #33CC00;
                    padding-right: 3px;
                    padding-left: 3px;
                    letter-spacing: 0px;
                    display:inline;
                }
                .yellow, .yellowcell {
                    font-weight: bold;
                    color: #000000;
                    background-color: #FFFF00;
                    padding-right: 3px;
                    padding-left: 3px;
                    letter-spacing: 0px;
                    display:inline;
                }
                .red, .redcell {
                    font-weight: bold;
                    color: #FFFFFF;
                    background-color: #FF0000;
                    padding-right: 3px;
                    padding-left: 3px;
                    letter-spacing: 0px;
                    display:inline;
                }
                .noscore, .noscorecell {
                    font-weight: bold;
                    color: #000000;
                    background-color: #808E9B;
                    padding-right: 3px;
                    padding-left: 3px;
                    letter-spacing: 0px;
                }
                #bigpic, button {
                    display:none;
                }
                #metascore, #userscore, .entity {
                    display:inline;
                }
                #userscore:before {
                    content: 'Userscore: ';
                }
                #scoredescription {
                    margin-left: -3px;
                }
                #scores:before {
                    content: 'Metascore: ';
                }
                #scoredescription, #scoreinfo {
                    background: none; font-weight:normal; display:inline;
                }
                p {
                    margin:0px;
                }
                .reviewbody, .publication, .quote {display:inline}
                .review { margin-bottom: 5px; }
                .publication:after { content: ':'; }
            </style>
            """


class MetacriticFile_v2(TextFile):
    def __init__(self, text):
        self.log("init")
        tmptext = ""

        s = re.search('(<div class="summary_wrap".*?)(<div id="side"|<div class="nrelate_wrapper)', text, re.S)  # text
        if s:
            tmptext += s.group(1)

        tmptext = re.sub('(?s)(<div class="label">Your Score.*?</ul>)', '', tmptext)
        tmptext = re.sub('Log in to finish rating Crimson', '', tmptext)
        tmptext = re.sub('<div class="rating_signin_tmpl">.*?<div class="section',
                         '<div class="section', tmptext, 0, re.S)

        self.text = '<div id="wiki_box-body" class="box-body">' + tmptext + '</div>'

        self.css += """
            <meta http-equiv="Content-Type" content="text/html; charset=utf8">
            <base href="http://www.metacritic.com/">
            <style type="text/css">
                body, td, h1, h2, h3 { font-size:50%; }
                .product_details { border-top: 1px dotted currentColor; }
                .author_reviews { display:none }
                .review_helpful { display:none }
                .review_grade { float:right }
                .review_critic { float:left }
                .review_body { clear:both }
                .review_content { border-top: 1px dotted currentColor; padding: 5px; }
                .blurb_expanded { display:inline }
                .toggle_expand_collapse { display:none }
                li { list-style-type: none; }
                ul,ol { padding-left:10px; }
            </style>
            """

