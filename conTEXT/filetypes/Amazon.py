import re
from Text import TextFile

config = {
    'base': "http://www.amazon.com",
    'search': "/s/ref=nb_sb_ss_i_0_13?url=search-alias%%3Dpopular&field-keywords=%s",
    'search_with_album': True,
    'link': 'a class="title" href="http://www.amazon.com(/[^"]*)">%s( \(.*?\)| \[.*?\])?</a>'
}


def matches(text):
    return '<title>Amazon.com' in text


class AmazonFile(TextFile):
    def __init__(self, text):
        self.log("init")
        tmptext = ""

        # 1. look for editorial + customer reviews
        endTagWithCustRev = '<div id="ftWR"'
        endTagNoCustRev = '<strong>Write a customer review'
        s = re.search('(<div class="bucket" id="productDescription">.*?)' + endTagWithCustRev, text, re.S)
        if s:
            tmptext += s.group(1)
        else:
            # 2. look ONLY for customer reviews
            s = re.search('(<div class="reviews".*?)' + endTagWithCustRev, text, re.S)
            if s:
                tmptext += s.group(1)
            else:
                # 3. look ONLY for editorial reviews
                s = re.search('(<div class="bucket" id="productDescription">.*?)' + endTagNoCustRev, text, re.S)
                if s:
                    tmptext += s.group(1)

        tmptext = re.sub('line-height:[ 0-9]*px', '', tmptext)
        tmptext = re.sub('font-size:[ 0-9]*px', '', tmptext)
        tmptext = re.sub('font-style:italic', '', tmptext)
        tmptext = re.sub('margin: 0 30px 0 25px', '', tmptext)
        tmptext = re.sub('margin:15px 0 0 25px', '', tmptext)
        tmptext = re.sub('padding-bottom: 22px', 'padding-bottom: 5px', tmptext)
        tmptext = re.sub('background-color:#f4f4cf;', 'background:rgba(200,200,200,0.5);', tmptext)
        tmptext = re.sub('background-color:#ffcc66; height:19px', 'background-color:#ffcc66; height:15px', tmptext)
        tmptext = re.sub('color:#333', '', tmptext)
        tmptext = re.sub('width:70%', '', tmptext)

        self.text = '<div id="wiki_box-body" class="box-body">' + tmptext + '</div>'

        self.css += """
            <base href="http://www.amazon.com/">
            <style type="text/css">
                .acrRating {display:none}
                .reviews .histoFullBar {margin: 1px;}

/*copied*/
.swSprite {
background: url("http://g-ecx.images-amazon.com/images/G/01/common/sprites/sprite-site-wide-3._V375430972_.png") no-repeat transparent;
display: inline-block;
margin: 0px;
overflow: hidden;
padding: 0px;
position: relative;
vertical-align: middle;
}
.swSprite span { position: absolute; left: -9999px; }
.reviews .fl {
float: left;
}
.reviews .clearboth {
clear: both;
}
.reviews .block {
display: block;
}
.reviews .mt15 {
margin-top: 15px;
}
.s_starBrandBigFull  { background-position: -280px -261px; width: 32px;height: 30px; }
.s_starBrandBigHalf  { background-position: -244px -261px; width: 32px;height: 30px; }
.s_starBrandBigEmpty { background-position: -211px -261px; width: 32px;height: 30px; }
.s_starBrandSmallFull  { background-position: -52px -299px; width: 16px;height: 15px; }
.s_starBrandSmallHalf  { background-position: -68px -299px; width: 16px;height: 15px; }
.s_starBrandSmallEmpty { background-position: -84px -299px; width: 16px;height: 15px; }
.s_starSmallFull  { background-position: -30px 0px; width: 13px;height: 13px; }
.s_starSmallHalf  { background-position: -82px -20px; width: 13px;height: 13px; }
.s_starSmallEmpty { background-position: -95px 0px; width: 13px;height: 13px; }
.s_star_0_0 { background-position: -95px 0px; width: 65px;height: 13px; }
.s_star_0_5 { background-position: -82px -20px; width: 65px;height: 13px; }
.s_star_1_0 { background-position: -82px 0px; width: 65px;height: 13px; }
.s_star_1_5 { background-position: -69px -20px; width: 65px;height: 13px; }
.s_star_2_0 { background-position: -69px 0px; width: 65px;height: 13px; }
.s_star_2_5 { background-position: -56px -20px; width: 65px;height: 13px; }
.s_star_3_0 { background-position: -56px 0px; width: 65px;height: 13px; }
.s_star_3_5 { background-position: -43px -20px; width: 65px;height: 13px; }
.s_star_4_0 { background-position: -43px 0px; width: 65px;height: 13px; }
.s_star_4_5 { background-position: -30px -20px; width: 65px;height: 13px; }
.s_star_5_0 { background-position: -30px 0px; width: 65px;height: 13px; }
.s_chevron { background-position: -30px -40px; width: 11px; height: 11px; }
.s_goTan { background-position: -50px -40px; width: 21px; height: 21px; }
.s_email { background-position: -80px -40px; width: 16px; height: 11px; }
.s_rss { background-position: -100px -40px; width: 12px; height: 12px; }
.s_extLink { background-position: -120px -40px; width: 15px; height: 13px; }
.s_close { background-position: -140px -40px; width: 15px; height: 15px; }
.s_collapseChevron { background-position: -30px -60px; width: 9px; height: 9px; }
.s_expandChevron { background-position: -40px -60px; width: 9px; height: 9px; }
.s_comment { background-position: -80px -60px; width: 16px; height: 15px; }
.s_expand { background-position: -100px -60px; width: 14px; height: 14px; }
.s_collapse { background-position: -120px -60px; width: 14px; height: 14px; }
.s_shvlBack { background-position: -30px -80px; width: 25px; height: 50px; }
.s_shvlBackClick { background-position: -30px -130px; width: 25px; height: 50px; }
.s_shvlNext { background-position: -60px -80px; width: 25px; height: 50px; }
.s_shvlNextClick { background-position: -60px -130px; width: 25px; height: 50px; }
.s_shvlBackSm { background-position: -90px -80px; width: 20px; height: 40px; }
.s_shvlBackSmClick { background-position: -90px -120px; width: 20px; height: 40px; }
.s_shvlNextSm { background-position: -110px -80px; width: 20px; height: 40px; }
.s_shvlNextSmClick { background-position: -110px -120px; width: 20px; height: 40px; }
.s_play { background-position: -140px -80px; width: 20px; height: 20px; }
.s_pause { background-position: -140px -100px; width: 20px; height: 20px; }
.s_playing { background-position: -140px -120px; width: 20px; height: 20px; }
.s_pausing { background-position: -140px -140px; width: 20px; height: 20px; }
.s_blueClearX { background-position: -170px 0px; width: 12px; height: 12px; }
.s_blueStar_0_0 { background-position: -255px 0px; width: 65px; height: 13px; }
.s_blueStar_1_0 { background-position: -242px 0px; width: 65px; height: 13px; }
.s_blueStar_2_0 { background-position: -229px 0px; width: 65px; height: 13px; }
.s_blueStar_3_0 { background-position: -216px 0px; width: 65px; height: 13px; }
.s_blueStar_4_0 { background-position: -203px 0px; width: 65px; height: 13px; }
.s_blueStar_5_0 { background-position: -190px 0px; width: 65px; height: 13px; }
.s_notify { background-position: -0px -190px; width: 25px; height: 25px; }
.s_confirm { background-position: -30px -190px; width: 25px; height: 25px; }
.s_alert { background-position: -60px -190px; width: 25px; height: 25px; }
.s_error { background-position: -90px -190px; width: 25px; height: 25px; }
.s_notifySm { background-position: -120px -190px; width: 17px; height: 17px; }
.s_confirmSm { background-position: -140px -190px; width: 17px; height: 17px; }
.s_alertSm { background-position: -160px -190px; width: 17px; height: 17px; }
.s_errorSm { background-position: -180px -190px; width: 17px; height: 17px; }
.s_checkDisabled { background-position: -150px -170px; width: 14px;height: 14px; }
.s_checkUnmarked { background-position: -90px -170px; width: 14px;height: 14px; }
.s_checkHover { background-position: -110px -170px; width: 14px;height: 14px; }
.s_checkMarked { background-position: -130px -170px; width: 14px;height: 14px; }
.s_amznLogo { background-position: -170px -20px; width: 127px; height: 26px; }
.s_primeBadge { background-position: -170px -50px; width: 45px; height: 13px; }
.s_add2CartSm { background-position: -170px -70px; width: 76px; height: 17px; }
.s_add2WishListSm { background-position: -170px -90px; width: 96px; height: 17px; }
.s_buyWith1ClickSm { background-position: -170px -110px; width: 96px; height: 17px; }
.s_preorderThisItemSm { background-position: -170px -130px; width: 108px; height: 17px; }
.s_seeBuyingOptionsSm { background-position: -170px -150px; width: 122px; height: 17px; }
.s_amznLikeBeak { background-position: -260px -200px; width: 12px; height: 10px; }
.s_amznLikeButtonOff { background-position: -210px -170px; width: 47px; height: 20px; }
.s_amznLikeButtonPressed { background-position: -210px -190px; width: 47px; height: 20px; }
.s_amznLikeButtonOn { background-position: -260px -170px; width: 47px; height: 20px; }

.s_starBigFull   { background-position: -78px -259px; width: 20px;height: 18px; }
.s_starBigHalf   { background-position: -78px -279px; width: 20px;height: 18px; }
.s_starBigEmpty { background-position: -97px -259px; width: 20px;height: 18px; }
.s_starBig_0_0 { background-position: -98px -259px; width: 95px;height: 18px; }
.s_starBig_0_5 { background-position: -79px -279px; width: 95px;height: 18px; }
.s_starBig_1_0 { background-position: -79px -259px; width: 95px;height: 18px; }
.s_starBig_1_5 { background-position: -60px -279px; width: 95px;height: 18px; }
.s_starBig_2_0 { background-position: -60px -259px; width: 95px;height: 18px; }
.s_starBig_2_5 { background-position: -41px -279px; width: 95px;height: 18px; }
.s_starBig_3_0 { background-position: -41px -259px; width: 95px;height: 18px; }
.s_starBig_3_5 { background-position: -22px -279px; width: 95px;height: 18px; }
.s_starBig_4_0 { background-position: -22px -259px; width: 95px;height: 18px; }
.s_starBig_4_5 { background-position: -3px  -279px; width: 95px;height: 18px; }
.s_starBig_5_0 { background-position: -3px  -259px; width: 95px;height: 18px; }

            </style>
            """

