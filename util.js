var msg = function (str) {
    Amarok.debug(str);
};

var toUtf8 = function (bytes) {
    var codec = QTextCodec.codecForName(new QByteArray("UTF-8"));
    return codec.toUnicode(bytes);
};

var timeout = function (func, interval, onlyOnce) {
    var qo = new QObject();
    qo.event = function (qevent) {
//        msg("timeout, calling: " + func);
        func();
        if (onlyOnce)
            this.killTimer(qo.timerID);
    };
    qo.timerID = qo.startTimer(interval);
    return qo;
};
