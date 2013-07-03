//var icon_rating			= new QIcon(Amarok.Info.scriptPath() + "/smallerstar.png");
//var icon_score			= new QIcon(Amarok.Info.iconPath( "love-amarok", 16));

function MainTab() {
    this.mutex = new QMutex(1);
}

MainTab.prototype.draw = function(parentWidget) {
    msg("Drawing main tab...");
    this.mainLayout = new QVBoxLayout(parentWidget);

    this.webView = new QWebView(parentWidget);
    this.webView.load(new QUrl(Amarok.Info.scriptPath() + "/main.html"));
    this.webView.contextMenuEvent = function (event) {
        // swallow
    };

    this.mainLayout.addWidget(this.webView, 0, 0);
};

MainTab.prototype.evalJS = function(js) {
    var safeJs;
    if (config.debug) {
        safeJs = "try{%s}catch(e){alert(e)}".replace(/%s/, js);
        msg(safeJs);
    } else {
        safeJs = "try{%s}catch(e){}".replace(/%s/, js);
    }
    return this.webView.page().mainFrame().evaluateJavaScript(safeJs);
};