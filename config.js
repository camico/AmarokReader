function Config() {
    // constants
    this.scriptName = "Amarok Reader";
    this.autostartLabel = "Autostart " + this.scriptName;
    this.icon = "amarok_lyrics";
    this.separator = "~~";

    this.debug = false;
}

Config.prototype.loadConfig = function (key, def) {
    return Amarok.Script.readConfig(key, String(def));
};

Config.prototype.saveConfig = function (key, value) {
    Amarok.Script.writeConfig(key, String(value));
};

Config.prototype.saveBoolean = function (aname, value) {
    if (value)
        this.saveConfig(aname, "true");
    else
        this.saveConfig(aname, "false");
};

Config.prototype.loadBoolean = function (key, def) {
    var val;
    if (def)
        val = this.loadConfig(key, "true");
    else
        val = this.loadConfig(key, "false");

    return val === "true";
};

Config.prototype.save = function () {
    msg("save config");
    this.saveBoolean("autostart", this.autostart);
    msg("done");
};

Config.prototype.load = function () {
    msg("load config");
    this.autostart = this.loadBoolean("autostart", true);

    msg(" autostart: " + this.autostart);
    msg("done");
};