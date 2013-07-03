import os

DEBUG = True
DATADIR = os.path.join(os.path.dirname(__file__), ".data")
LOGFILE = os.path.join(DATADIR, "log")
CFGFILE = os.path.join(DATADIR, "config")
TMPDIR = os.path.join(DATADIR, "tmp")
ALBUM = 1
ARTIST = 2


# utility commands, used in emergency situations, with nearly zero dependencies
def run(command, *args):
    arguments = command.split()
    for a in args:
        arguments.append(a)
    return os.spawnlp(os.P_WAIT, arguments[0], *arguments)


def popup(errmsg):
    if run("kdialog", "--error", errmsg) != 0:
        run("xmessage", errmsg)


def tounicode(string):
    if string is None:
        return None

    #return unicode(string,locale.getpreferredencoding())
    return unicode(string, 'latin1')
