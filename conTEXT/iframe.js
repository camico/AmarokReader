var basehref = function () {
    return document.getElementsByTagName('base')[0].href;
};

var adjustIframeHeight = function () {
    parent.resizeIframe(document.body.scrollHeight);
};

parent.resetIframeHeight();
document.addEventListener('DOMContentLoaded', adjustIframeHeight, false);
