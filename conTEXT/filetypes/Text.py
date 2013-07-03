import logging
import re


class TextFile:
    injectable = False
    css = ""
    text = ""
    unmodifiedtext = ""

    def __init__(self, text):
        self.log("init")
        self.injectable = True
        self.unmodifiedtext = text

        text = re.sub("\r", "", text)
        text = re.sub("<", "&lt;", text)
        text = re.sub(">", "&gt;", text)
        text = text.strip('\n\x0b\x0c\r').replace('\t', '  ')
        self.text = '<div class="box-body">' + text + '</div>'

    def wrap(self):
        self.text = re.sub("\n", "<br>", self.text)

    def log(self, msg=""):
        logger = logging.getLogger(str(self.__class__).replace('filetypes.', ''))
        logger.debug(msg)


class NFOFile(TextFile):
    def __init__(self, text):
        TextFile.__init__(self, text)
        self.log("init")
        self.text = re.sub('<div c', '<pre c', self.text)
        self.text = re.sub('</div>', '</pre>', self.text)

        self.css = """
            <style type="text/css">
                pre {
                    font-family: Lucida ConsoleP;
                    font-size: 7.5pt;
                    line-height: 1em;
                }
            </style>
            """


class HTMLFile(TextFile):
    def __init__(self, text):
        self.log("init")
        text = re.sub("<html.*>", "", text);
        text = re.sub("<head.*>", "", text);
        text = re.sub("<body.*>", "", text);
        text = re.sub("</body>", "", text);
        text = re.sub("</head>", "", text);
        text = re.sub("</html>", "", text);

        self.text = '<div id="wiki_box-body" class="box-body">' + text + '</div>'

        self.css = """
            <style type="text/css">
                * {font-size:95%;}
            </style>
            """
