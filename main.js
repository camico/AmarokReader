/*
Amarok Reader main script
(c) 2013 <camico@users.sourceforge.net>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
*/

var imp1 = Importer.loadQtBinding("qt.core");
var imp2 = Importer.loadQtBinding("qt.gui");
var imp3 = Importer.loadQtBinding("qt.webkit");
if (!(imp1 && imp2 && imp3))
    Amarok.alert('Could not load necessary QT bindings. You probably need at least Amarok 2.6.', 'sorry');

Importer.include("config.js");
Importer.include("window.js");
Importer.include("util.js");

var Main = function () {
    var python;
    var pythonCmd = "python " + Amarok.Info.scriptPath() + "/conTEXT/conTEXT.py";
    var mainWindow;
    var timer;
    var lastCmd = null;
    var that = this;
    var error = "Could not start python script. Please check your python installation and\n" +
        "- the output obtained by running 'amarok --debug' in a console\n" +
        "- the output obtained by running '" + pythonCmd + "' in a console.";

    this.shutdown = function () {
        msg("Main.shutdown");
        timer.killTimer(timer.timerID);
        python.kill();
    };

    this.feed = function (cmd) {
        if (python && mainWindow.isOpen() && cmd != lastCmd) {
            python.write(new QByteArray(cmd + "\n"));
            lastCmd = cmd;
        }
    };

    this.digest = function () {
        var bytes = python.readAllStandardOutput();
        var str = toUtf8(bytes);
//        msg("digest str: " + str);

        var jsStart, meStart, jsEnd, meEnd;
        while (str) {
            jsStart = str.indexOf("/*<js>*/");
            meStart = str.indexOf("/*<me>*/");
            if (jsStart == 0) {
                jsEnd = str.indexOf("/*</js>*/") + 9;
                if (jsEnd == -1) // incomplete message, bailing out
                    break;
                that.evalJS(str.substring(jsStart, jsEnd));
                str = str.substring(jsEnd, str.length);
            }
            else if (meStart == 0) {
                meEnd = str.indexOf("/*</me>*/") + 9;
                if (meEnd == -1) // incomplete message, bailing out
                    break;
                that.showMessage(str.substring(meStart, meEnd));
                str = str.substring(meEnd, str.length);
            }
            else {
                msg("unknown message!");
                msg(str);
                break;
            }
        }
//        msg("digest complete");
    };

    this.stateChanged = function (state) {
        switch (state) {
            case QProcess.NotRunning:
                if (mainWindow.isOpen())
                    Amarok.alert(error, "sorry");
        }
        msg("python state: " + state);
    };

    this.showWindow = function () {
        if (mainWindow && mainWindow.isOpen()) {
            Amarok.alert(config.scriptName + " window is already open!");
            return;
        }

        msg("Showing main window...");
        mainWindow = new MainWindow();
        mainWindow.show();

        python = new QProcess(mainWindow);
        msg("Starting python...");
        python.stateChanged.connect(that.stateChanged);
        python.start(pythonCmd);
        if (!python.waitForStarted()) {
            Amarok.alert(error, "sorry");
        }
        python.readyReadStandardOutput.connect(that.digest);
        Amarok.Engine.trackChanged.connect(that.onTrackChange);
        that.onTrackChange(); //initial feed

        timer = timeout(function () {
            var cmds = main.evalJS("if (typeof getCommands !== 'undefined') getCommands()");
            if (cmds) {
//                msg(cmds);
                main.feed("getCommands" + config.separator + cmds);
            }
        }, 1000);
    };

    this.toggleAutostart = function () {
        var entry = Amarok.Window.SettingsMenu[config.autostartLabel];
        config.autostart = entry.checked;
        config.save();
    };

    this.evalJS = function (js) {
        return mainWindow.evalJS(js);
    };

    this.showMessage = function (str) {
        str = str.replace("/*<me>*/", "");
        str = str.replace("/*</me>*/", "<br>");
        Amarok.Window.Statusbar.longMessage(str);
    };

    this.onTrackChange = function() {
        msg("onTrackChange state: " + Amarok.Engine.engineState());
        main.feed("nowPlaying" + config.separator + Amarok.Engine.currentTrack().artist
            + config.separator + Amarok.Engine.currentTrack().album
            + config.separator + Amarok.Engine.currentTrack().url);
    };
};

///////////////////////////////////////////////////////////////////////////////

var main = new Main();
var config = new Config();
config.load();

if (Amarok.Window.addToolsMenu(config.scriptName, config.scriptName, config.icon)) {
    var toolsEntry = Amarok.Window.ToolsMenu[config.scriptName];
    toolsEntry['triggered()'].connect(main.showWindow);
} else {
    msg("tools menu entry already exists!");
}

if (Amarok.Window.addSettingsMenu(config.autostartLabel, config.autostartLabel, config.icon)) {
    var settingsEntry = Amarok.Window.SettingsMenu[config.autostartLabel];
    settingsEntry['triggered()'].connect(main.toggleAutostart);
    settingsEntry['checkable'] = true;
    settingsEntry['checked'] = config.autostart;
} else {
    msg("settings menu entry already exists!");
}

config.autostart && main.showWindow();
