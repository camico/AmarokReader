import re
from Text import TextFile

config = {
    'base': "http://www.plattentests.de",
    'search': "/suche.php?suche=%s&parameter=band",
    'eliminate': ['<b>', '</b>'],
    'link': 'Du hast nach.*?(rezi.php\?show=[0-9]+)">[^<>]*? %s</a>'
}


def matches(text):
    return '<title>Plattentests' in text


class PlattentestsFile(TextFile):
    def __init__(self, text):
        self.log("init")
        tmptext = ""

        # v2
        s = re.search("<div class=\"headerbox rezi\">(.*?)</div>", text, re.S)
        if s:
            tmptext += s.group(1)
            s = re.search("(<div id=\"rezitext\">.*?</div>)", text, re.S)  # Rezitext
            if s:
                tmptext += s.group(1)
            s = re.search("(<div id=\"rezihighlights\">.*?</div>)", text, re.S)  # Highlights
            if s:
                tmptext += s.group(1)
            s = re.search("(<div id=\"reziref\">.*?</div>)", text, re.S)  # refs
            if s:
                tmptext += s.group(1)
            s = re.search("(<div id=\"surftipps\">.*?</div>)", text, re.S)  # refs
            if s:
                tmptext += s.group(1)
            s = re.search("(<div id=\"reziweitere\">.*?)<div id=\"reziforum\">", text, re.S)  # refs
            if s:
                tmptext += s.group(1)
            s = re.search("(<div id=\"reziforum\">.*?</div>)", text, re.S)  # refs
            if s:
                tmptext += s.group(1)
        else:
            # v1
            s = re.search("(<span class=\"reziheader\">.*</span><br>)", text)  # Albumtitel
            if s:
                tmptext += s.group(1)
            s = re.search("(<span class=\"label\">.*</span><br>)", text)  # Label
            if s:
                tmptext += s.group(1)
            s = re.search("(<span class=\"wertung\">.*</span>)", text)  # VOE und Spielzeit
            if s:
                tmptext += s.group(1) + "<br>"
            s = re.search("(Unsere Bewertung: .*)<br>", text)
            if s:
                tmptext += s.group(1) + ", "
            s = re.search("(Eure.*-Bewertung:.*?<br>)", text, re.S)
            if s:
                tmptext += s.group(1) + "<br>"
            s = re.search("(<h1 align=\"center\" class=\"reziheader\">.*</h1>)", text)  # Rezititel
            if s:
                tmptext += s.group(1)
            s = re.search("(<p align=\"left\" class=rezitxt>.*</p>)", text, re.S)  # Rezitext
            if s:
                tmptext += s.group(1)
            s = re.search("(<span class=\"header\">Highlights:.*<br><br>)(<span|..<iframe)", text,
                          re.S)  # Highlights und Ref.
            if s:
                tmptext += s.group(1)
            s = re.search("(<span class=\"header\">Surftips:.*</span>)", text, re.S)  # Surftips
            if s:
                tmptext += s.group(1)

        tmptext = re.sub("target=\"_blank\"", "", tmptext)

        self.text = '<div id="wiki_box-body" class="box-body">' + tmptext + '</div>'

        self.css += """
            <style type="text/css">
                .reziheader {font-weight:bold;}
                .bewertung {display:inline;}
                .header {font-weight:bold;}
                .label {font-style:italic;}
                .cover {display:none;}
            </style>
            <base href="http://www.plattentests.de/">
            """
    # 	body, p, a, h1, h2, h3, h4 {font-size:50%;}


