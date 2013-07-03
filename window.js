Importer.include("main_tab.js");

function MainWindow() {
    var defaultWidth = 380;
    var defaultHeight = 400;

//    MainWindow.superclass.call(this);
    QMainWindow.call(this, null);

    this.windowTitle = config.scriptName;
//    this.mainTabWidget = new QTabWidget();
    this.mainWidget = new QWidget();
//    this.configurationWidget = new QWidget();
    this.mainTab = new MainTab();

//    config.draw(this.configurationWidget);
//    config.showConfiguration();
    this.mainTab.draw(this.mainWidget);

//    this.mainTabWidget.documentMode = true;
//    this.mainTabWidget.addTab(this.mainWidget, qsTr("Reviews"));
//    this.mainTabWidget.setTabEnabled(0, false);
//    this.mainTabWidget.addTab(this.configurationWidget, qsTr("Config"));

//    config.buttonBox.clicked.connect(this, this.applyPressed);

//    this.setCentralWidget(this.mainTabWidget);
    this.setCentralWidget(this.mainWidget);
    this.open = true;
    this.resize(defaultWidth, defaultHeight);
}

MainWindow.prototype = new QMainWindow();

//MainWindow.prototype.applyPressed = function () {
//    config.onConfigurationApply();
//    this.mainTabWidget.setCurrentIndex(0);
//};

MainWindow.prototype.closeEvent = function (CloseEvent) {
    msg("closing window...");
    this.open = false;
    main.shutdown();
//    for (var i = 0; i < 2; i++) {
//        tabWidget.removeTab(0);
//    }
    CloseEvent.accept();
    msg("done");
};

//MainWindow.prototype.resizeEvent = function (ResizeEvent) {
//    msg("resizing window...");
//    this.displayCommon.changeFrameWidth(ResizeEvent.size().width() - 64);
//};

MainWindow.prototype.evalJS = function(js) {
    return this.mainTab.evalJS(js);
};

MainWindow.prototype.isOpen = function() {
    return this.open;
};