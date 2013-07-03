import re
from Text import TextFile

config = {
    'google': True,
    'extra_term': 'Album',
    'extra_check': 'class="review"'
}


def matches(text):
    return '<title> Rolling Stone' in text or \
           'Rolling Stone</title>' in text or \
           'Rolling Stone Music | Music Reviews</title>' in text


class RollingStoneFile(TextFile):
    def __init__(self, text):
        self.log("init")
        tmptext = ""
        s = re.search('(<div class="header-top.*?)<div id="content-bottom">', text, re.S)  # title and data
        if s:
            tmptext += s.group(1)
        else:
            s = re.search('(<div id="musicReview".*?)<!-- start: feature community review -->', text, re.S)  # v2
            if s:
                tmptext += s.group(1)
                tmptext = re.sub('(?s)(<div id="mostPopular".*?)<div id="storyTextContainer"',
                                 '<div id="storyTextContainer"', tmptext)
            else:
                s = re.search('(<div id="main".*?)<p><strong>Related', text, re.S)  # v3
                if s:
                    tmptext += s.group(1)

        # make ratings work (url hack)
        s = re.search('pageurl=(.*?);', text, re.S)
        if s:
            pageurl = s.group(1)
            s = re.search('<input type="hidden" name="rating_content_id".*?value="(.*?)"', tmptext, re.S)
            if s:
                content_id = s.group(1)
                tmptext = re.sub('function setRating\(id\) {', 'function setRating(id) {' +
                                                               'parent.openURL(basehref()+"' + pageurl + '?rating_content_id=' + content_id +
                                                               '&rating_' + content_id + '_5="+id);',
                                 tmptext)
            tmptext = re.sub('<form name="monorating"', '<form name="monorating" target="_blank"', tmptext)

        tmptext = re.sub('height="250"', 'height="0"', tmptext)
        tmptext = re.sub('Average User Rating', '<br>Average User Rating', tmptext)
        tmptext = re.sub('of 5 Stars', ' of 5 Stars', tmptext)
        tmptext = re.sub('<P>', '', tmptext)
        tmptext = re.sub('<p class="artist">', '<span class="artist">', tmptext)
        tmptext = re.sub('<p class="albumtitle">', '<span class="albumtitle">', tmptext)
        tmptext = re.sub('</p></h1>', '</span></h1>', tmptext)
        tmptext = re.sub('Advertisement', '', tmptext)
        tmptext = re.sub('(?si)<IFRAME.*?</IFRAME>', '', tmptext)
        tmptext = re.sub('(?si)<div class="tracklist">.*?<div class="simplefeature yourturnwide">',
                         '<div class="simplefeature yourturnwide">', tmptext)
        tmptext = re.sub('<img.*?</img>', '', tmptext)
        tmptext = re.sub('(?s)<p class="useful".*?</p>', '', tmptext)
        tmptext = re.sub('(?s)<p class="rate".*?</p>', '<hr>', tmptext)

        #v3
        tmptext = re.sub('Listen To .*?</strong>', '', tmptext)
        tmptext = re.sub('star rating</span>', '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
                                               '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>', tmptext)

        self.text = '<div id="wiki_box-body" class="box-body">' + tmptext + '</div>'

        self.css += """
            <base href="http://www.rollingstone.com/">
            <style type="text/css">
                /*body, p, td, font, span, div, h1, h2, h3, h4 { font-size:50%; }*/
                .listen, .ad, .share-menu, .more-cdreviews, .user-rating { display:none }
                #newsandreviewswidget { display:none }
                .user-rating {margin:0;padding:0;border:2px solid; width:339px; height:34px;background-color:#906;}

                input[type="radio"] { width:12px; }
                ul { padding:0 }
                .headerImgHolder { display:none }

                /* v3 */
                .reviewSection-Image { display:none }
                h3,h4,h5 { margin:0; padding:0 }
                .socialActionsTopWrapper { display:none }
                .community, #communityRating { display:none }

/* rating stuff, copied 1:1 */

.fullFourStarRatings-Red {
  background: url(http://assets.rollingstone.com/images/fe/sprite/fullstar-red.gif) no-repeat;
  width: 65px;
  text-indent: -9999px;
}
.fullFourStarRatings-Orange {
  background: url(http://assets.rollingstone.com/images/fe/sprite/fullstar-orange.gif) no-repeat;
  width: 65px;
  text-indent: -9999px;
}
.fullFiveStarRatings-Red {
  background: url(http://assets.rollingstone.com/images/fe/sprite/fullstar-red.gif) no-repeat;
  width: 81px;
  text-indent: -9999px;
}
.fullFiveStarRatings-Orange {
  background: url(http://assets.rollingstone.com/images/fe/sprite/fullstar-orange.gif) no-repeat;
  width: 81px;
  text-indent: -9999px;
}
.oneStar {
  background-position: -64px 0
}
.twoStar {
  background-position: -48px 0;
}
.threeStar {
  background-position: -32px 0;
}
.fourStar {
  background-position: -16px 0;
}
.fiveStar {
  background-position: 0 0;
}
.noStar {
  background: url(/images/fe/zero_stars_music.png) 0 0 no-repeat;
}
.moviesChannel .noStar {
  background: url(/images/fe/zero_stars_movies.png) 0 0 no-repeat;
}
.fullFourStarRatings-Red.notRated {
  width: 74px;
  height: 16px;
  background-position: 0 -16px
}
.fullFiveStarRatings-Red.notRated {
  width: 80px;
  height: 16px;
  background-position: 0 -32px
}
.fullFourStarRatings-Orange.notRated {
  width: 74px;
  height: 16px;
  background-position: 0 -16px
}
.fullFiveStarRatings-Orange.notRated {
  width: 80px;
  height: 16px;
  background-position: 0 -32px
}
.halfFourStarRatings-Red {
  background: url(http://assets.rollingstone.com/images/fe/sprite/halfstar-red.gif) no-repeat;
  width: 65px;
  text-indent: -9999px;
}
.halfFourStarRatings-Orange {
  background: url(http://assets.rollingstone.com/images/fe/sprite/halfstar-orange.gif) no-repeat;
  width: 65px;
  text-indent: -9999px;
}
.halfFiveStarRatings-Red {
  background: url(http://assets.rollingstone.com/images/fe/sprite/halfstar-red.gif) no-repeat;
  width: 81px;
  text-indent: -9999px;
}
.halfFiveStarRatings-Orange {
  background: url(http://assets.rollingstone.com/images/fe/sprite/halfstar-orange.gif) no-repeat;
  width: 81px;
  text-indent: -9999px;
}
.halfStar {
  background-position: -64px 0
}
.oneHalfStar {
  background-position: -48px 0;
}
.twoHalfStar {
  background-position: -32px 0;
}
.threeHalfStar {
  background-position: -16px 0;
}
.fourHalfStar {
  background-position: 0 0;
}
.noStarRed {
  background: url(/images/fe/zero_stars_movies.png) 0 0 no-repeat;
}
.fullFourStarRatings-Red.noStar {
  background: url(/images/fe/zero_stars_movies.png) 0 0 no-repeat;
}
/* End Review Page*/

</style>
"""
