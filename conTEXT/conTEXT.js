/*
conTEXT.js
part of conTEXT Amarok script
*/
var frame = 0;
var numfiles = 0;
var anim;
var searchSite = "";
var clickedURL = "";
var file2edit = "";
var file2trash = "";
var searchnow = "";
var scrollArrows = ["arrow_u", "arrow_d", "arrow_b", "arrow_t"];

function get(e) { return document.getElementById(e); }
function make(e) { return document.createElement(e); }
function text(e) { return document.createTextNode(e); }

function info(num) {
    var path, mesg;
    switch(num) {
        case -1:
            clearTimeout(anim);
            mesg = "Amarok Reader: searching...";
            path = paramBasepath + "/search0.png";
            anim = setTimeout("animateIcon()", 500);
            removeInfo();
            break;
        case 0:
            clearTimeout(anim);
            mesg = "Amarok Reader: no files";
            path = paramBasepath + "/icon0.png";
            numfiles = num;
            removeInfo();
            togglePlaceHolder(true);
            break;
        default:
            clearTimeout(anim);
            mesg = "Amarok Reader: showing " + num + (num == 1 ? " file" : " files");
            path = paramBasepath + "/icon1.png";
            numfiles = num;
            removeInfo();
            togglePlaceHolder(false);
            break;
    }

    var inf = make('div');
    inf.setAttribute('id', 'conTEXT_info');
//        inf.setAttribute('style', 'position:fixed; bottom:-1px; right:-1px; z-index:100; ' +
//            'padding-top:3px; padding-left: 0px; opacity:0.75;');
    inf.setAttribute('style', 'position:fixed; top:2px; left:2px; z-index:100; opacity:0.9; padding-bottom:2px;');
    inf.setAttribute('title', mesg);
    inf.setAttribute('onmouseover', 'showSearchMenu()');
    inf.setAttribute('onclick', 'toggleSearchMenu()');

    var img = make('img');
    img.setAttribute('id', 'conTEXT_icon');
    img.setAttribute('src', path);
    inf.appendChild(img);

    var body = get('body');
    body.appendChild(inf);
    body.setAttribute('style', 'margin:0; font:' + paramFont);

    var bg = get('conTEXT_logo');
    bg.src = paramBasepath + "/amarok2.png";

    for (var a in scrollArrows) {
        get(scrollArrows[a]).src = "file:" + paramBasepath + "/" + scrollArrows[a] + ".png";
    }
}

function animateIcon() {
    get('conTEXT_icon').src = paramBasepath + "/search" + (frame % 4) + ".png";
    frame += 1;
    anim = setTimeout("animateIcon()", 500);
}

function showSearchMenu() {
    if (get('conTEXT_search')) return;

    var popup = make('div');
    popup.setAttribute('id', 'conTEXT_search');
    popup.setAttribute('onmouseover', 'showSearchMenu()');
//    	popup.setAttribute('onmouseleave', 'removeSearchMenu()');

    var search = make('div');
    addEvent(search, 'mouseleave', removeSearchMenu);
    var backgroundColor = 'rgba(245,245,245,0.95)';
    var backgroundHover = 'rgba(210,210,210,0.95)';
//        search.setAttribute('style', 'position:fixed; bottom:14px; right:0px; z-index:100; ' +
//            'background:'+backgroundImage+'; color:black; border:1px outset black; ' +
//            'font-weight:bold; text-align:left; white-space:nowrap; padding-left:3px;');
    search.setAttribute('style', 'position:fixed; top:19px; left:2px; z-index:100; ' +
        'background:'+backgroundColor+'; color:black; border:1px solid #aaa; ' +
        'font-weight:bold; text-align:left; white-space:nowrap; padding-left:3px; padding-right:2px; border-radius:3px;');

    var c = make('div');
    c.setAttribute('style', 'float:right; font-weight:bold; font-style:italic; cursor:pointer;');
    c.setAttribute('onmouseover', 'showSearchMenu()');
    c.setAttribute('onclick', 'toggleAll()');
    c.setAttribute('title', 'Auto-search all sites on album change');
    c.appendChild(text("Auto"));
    search.appendChild(c);
    search.appendChild(text("Search reviews"));

    var sites = searchSites.split(" ");
    for (var i = 0; i < sites.length; i++) {
        var site = sites[i].split(":");
        if (mustHide(site[0]))
            continue;
        var s = make('div');
        s.setAttribute('id', 'conTEXT_search_'+site[0]);
        s.setAttribute('style', 'border-top:1px dotted gray; font-weight:normal; padding-right:20px; ' +
            'cursor:pointer;');
        s.setAttribute('onmouseover', 'this.style.background="'+backgroundHover+'"; showSearchMenu()');
        s.setAttribute('onmouseout', 'this.style.background="transparent"; showSearchMenu()');
         c = make('div');
         c.setAttribute('id', 'conTEXT_autosearch_'+site[0]);
         c.setAttribute('style', 'float:right; margin-right:-20px; margin-top:3px;');
         c.setAttribute('onclick', 'toggleAutoSearch("'+site[0]+'");');
         c.setAttribute('title', 'Auto-search '+site[0]);
          var img = make('img');
          if (site[1]=="True")
            img.setAttribute('src', paramBasepath+'/check1.png');
          else
            img.setAttribute('src', paramBasepath+'/check0.png');
         c.appendChild(img);
        s.appendChild(c);
         var t = make('div');
         t.setAttribute('onclick', 'doSearch("'+site[0]+'"); this.lastChild.data="Searching..."; this.style.color="gray";');
         t.setAttribute('title', 'Search '+site[0]+' now');
         t.appendChild(text(site[0]));
        s.appendChild(t);
        search.appendChild(s);
    }
    popup.appendChild(search);

//        var backgroundColor = 'rgba(240,240,240,0.9)';
    var toolbar = make('div');
//        toolbar.setAttribute('style', 'position:fixed; bottom:0px; right:14px; z-index:100;');
    toolbar.setAttribute('style', 'position:fixed; top:2px; left:20px; z-index:100;');
    toolbar.setAttribute('onmouseover', 'showSearchMenu()');
    img = make('img');
    img.setAttribute('src', paramBasepath+'/searchnow.png');
    img.setAttribute('onclick', 'searchNow()');
    img.setAttribute('title', 'Search all (or all marked) sites now!');
    img.setAttribute('style', 'cursor:pointer; background:'+backgroundColor+'; border-radius:3px; padding:3px 2px; margin-right:3px; margin-bottom:2px;');
    img.setAttribute('onmouseover', 'this.style.backgroundColor="'+backgroundHover+'"; showSearchMenu()');
    img.setAttribute('onmouseout', 'this.style.backgroundColor="'+backgroundColor+'";');
    toolbar.appendChild(img);
    if (numfiles > 0) {
      img = make('img');
      img.setAttribute('src', paramBasepath+'/edit.png');
      img.setAttribute('onclick', 'editFile()');
      img.setAttribute('title', 'Open current file externally');
      img.setAttribute('style', 'cursor:pointer; background:'+backgroundColor+'; border-radius:3px; padding:3px 2px; margin-right:3px; margin-bottom:2px;');
      img.setAttribute('onmouseover', 'this.style.backgroundColor="'+backgroundHover+'"; showSearchMenu()');
      img.setAttribute('onmouseout', 'this.style.backgroundColor="'+backgroundColor+'";');
      toolbar.appendChild(img);
      img = make('img');
      img.setAttribute('src', paramBasepath+'/trash.png');
      img.setAttribute('onclick', 'trashFile()');
      img.setAttribute('title', 'Move current file to trash');
      img.setAttribute('style', 'cursor:pointer; background:'+backgroundColor+'; border-radius:3px; padding:3px 2px; margin-right:3px; margin-bottom:2px;');
      img.setAttribute('onmouseover', 'this.style.backgroundColor="'+backgroundHover+'"; showSearchMenu()');
      img.setAttribute('onmouseout', 'this.style.backgroundColor="'+backgroundColor+'";');
      toolbar.appendChild(img);
    }
    popup.appendChild(toolbar);

//	ref = get('current_box');
//	ref.insertBefore(popup, ref.lastChild);
    var ref = document.getElementsByTagName('body')[0];
    ref.appendChild(popup);
}

function mustHide(site) {
    var hides = hideDomains.split(" ");
    for (j = 0; j < hides.length; j++) {
        if (site.substr(site.length - 4, 4) == hides[j] ||
            site.substr(site.length - 3, 3) == hides[j] ||
            site.substr(site.length - 2, 2) == hides[j]) {
            return true;
        }
    }
    return false;
}

function toggleAutoSearch(sitename) {
    var img = get("conTEXT_autosearch_" + sitename).lastChild;
    if(img.src.substr(img.src.length-5) == "0.png") {
        img.src = paramBasepath+"/check1.png";
        searchSites = searchSites.replace(sitename+":False",sitename+":True");
    } else {
        img.src = paramBasepath+"/check0.png";
        searchSites = searchSites.replace(sitename+":True",sitename+":False");
    }
}

function toggleAll() {
    var notAllSelected = /False/.test(searchSites);
    sites = searchSites.split(" ");
    for(i=0; i<sites.length; i++) {
        site = sites[i].split(":");
        sitename = site[0];
        if(notAllSelected) {
            try{ img = get("conTEXT_autosearch_"+sitename).lastChild;
                 img.src = paramBasepath+"/check1.png"; } catch(e){ }
            searchSites = searchSites.replace(sitename+":False",sitename+":True");
        } else {
            try{ img = get("conTEXT_autosearch_"+sitename).lastChild;
                 img.src = paramBasepath+"/check0.png"; } catch(e){ }
            searchSites = searchSites.replace(sitename+":True",sitename+":False");
        }
    }
}

function doSearch(sitename) {
    searchSite = sitename;
    anim = setTimeout("animateIcon()",500);
}

function searchNow() {
    var someSiteSelected = /True/.test(searchSites);
    if(!someSiteSelected) {
        toggleAll();
        searchnow = "SEARCH_ALL_TEMPORARY";
    } else {
        searchnow = "SEARCH_MARKED";
    }
    removeSearchMenu();
}

function openURL(url) {
    clickedURL = url;
}

function editFile() {
    file2edit = realfilenames[curindex];
    removeSearchMenu();
}

function trashFile() {
    file2trash = realfilenames[curindex];
//        if (numfiles==1)
//            undoInjection();
//        else
    if (numfiles != 1)
        removeSearchMenu();
}

function baseFilename(f) {
    var r = f.substr(f.lastIndexOf('/') + 1);
    r = r.substr(0, r.length - 5); // cut off the extra ".html"
    return r;
}

function getCommands() {
    var s = searchSite;
    var u = clickedURL;
    var e = file2edit;
    var t = file2trash;
    var n = searchnow;
    searchnow = "";
    searchSite = "";
    clickedURL = "";
    file2edit = "";
    file2trash = "";
    var f = typeof filenames !== 'undefined' && typeof curindex !== 'undefined' ? baseFilename(filenames[curindex]) : "";
    var ss = typeof searchSites !== 'undefined' ? searchSites : "";
    var p = conTEXTscrollpos = window.pageYOffset;
    return n+'|'+t+'|'+e+'|'+u+'|'+s+'|'+ss+'|'+f+'|'+p;
}

function searchSuccess(sitename) {
    var ref = get('conTEXT_search_'+sitename);
    if (ref) {
        ref.lastChild.lastChild.data = "...Found!";
        ref.lastChild.style.color = 'green';
    }
    info(numfiles);
}

function searchFailure(sitename) {
    var ref = get('conTEXT_search_'+sitename);
    if (ref) {
        ref.lastChild.lastChild.data = "...Not found!";
        ref.lastChild.style.color = 'red';
    }
    info(numfiles);
}

function searchError(sitename, msg) {
    var ref = get('conTEXT_search_'+sitename);
    if (ref) {
        ref.lastChild.lastChild.data = "...Error: " + msg;
        ref.lastChild.style.color = 'red';
    }
    info(numfiles);
}

function removeSearchMenu(/*delay*/) {
    var ref = get('conTEXT_search');
    if (ref) ref.parentNode.removeChild(ref);
}

function toggleSearchMenu() {
    var ref = get('conTEXT_search');
    if(ref)
        ref.parentNode.removeChild(ref);
    else
        showSearchMenu();
}

function removeInfo() {
    var ref = get('conTEXT_info');
    if (ref) ref.parentNode.removeChild(ref);
}

function togglePlaceHolder(show) {
    var ref = get('conTEXT_placeholder');
    if (ref) ref.style.display = show ? 'block' : 'none';

    if (show) {
        // hide all previously displayed content
        ref = get('conTEXT_box');
        if (ref) ref.parentNode.removeChild(ref);
    }
    for (var a in scrollArrows) {
        ref = get(scrollArrows[a]);
        if (ref) ref.style.display = show ? 'none' : 'inline';
    }
}

function addEvent(_elem, _evtName, _fn, _useCapture) {
    if (typeof _elem.addEventListener != 'undefined') {
        if (_evtName === 'mouseenter') {
            _elem.addEventListener('mouseover', mouseEnter(_fn), _useCapture);
        }
        else if (_evtName === 'mouseleave') {
            _elem.addEventListener('mouseout', mouseEnter(_fn), _useCapture);
        }
        else {
            _elem.addEventListener(_evtName, _fn, _useCapture);
        }
    }
    else if (typeof _elem.attachEvent != 'undefined') {
        _elem.attachEvent('on' + _evtName, _fn);
    }
    else {
        _elem['on' + _evtName] = _fn;
    }
}

function mouseEnter(_fn) {
    return function (_evt) {
        var relTarget = _evt.relatedTarget;
        if (this === relTarget || isAChildOf(this, relTarget)) {
            return;
        }
        _fn.call(this, _evt);
    }
}

function isAChildOf(_parent, _child) {
    if (_parent === _child) {
        return false;
    }
    while (_child && _child !== _parent) {
        _child = _child.parentNode;
    }
    return _child === _parent;
}

/*
  former ContextBrowserUpdater functions
*/

function showNext() {
	fileindex++;

	var filechanged = false;
    if (fileindex != curindex)
		filechanged = true;

    if (fileindex == filenames.length)
		fileindex = 0;

	var fname = filenames[fileindex];
    var fnameElm = get('conTEXT_file');
    if (fnameElm) {
        fnameElm.firstChild.data = fileNumber() + prettyFilename(fname);
        fnameElm.title = baseFilename(fname).length > filename_max ? baseFilename(fname) : "";
    }

	var node = get('conTEXT_content');
    if (node && filechanged) {
        // normal html mode, update iframe
        node.firstChild.style.display = 'none';
        node.lastChild.style.display = 'block';
        node.lastChild.src = fname;
    }
	curindex = fileindex;
}

function showPrev() {
    if (fileindex == 0) fileindex = filenames.length - 2;
	else fileindex -= 2;
	showNext();
}

function showFile(index) {
	fileindex = parseInt(index);
    if (fileindex == 0 || fileindex >= filenames.length)
		fileindex = -1;
	else
		fileindex--;
	curindex = fileindex;
	showNext();
}

function showFileWithName(name) {
    for (var i = 0; i < filenames.length; i++) {
        if (baseFilename(filenames[i]) == name) {
            showFile(i);
            return;
        }
    }
	showFile(0);
}

function wheelOnHeader(event) {
    if (event.wheelDelta < 0)
        showNext();
    else
        showPrev();
}

function resetIframeHeight() {
    get('conTEXT_iframe').style.height = conTEXTheight;
}

function resizeIframe(newHeight) {
    get('conTEXT_iframe').style.height = parseInt(newHeight) + 65;
}

function fileNumber() {
	var r = '';
    if (filenames.length > 0)
        r = '(' + String(fileindex + 1) + '/' + filenames.length + ') ';
    return r;
}

function prettyFilename(f) {
    filename_max = (filenames.length > 1 /*|| resizing*/) ? 30 : 35;
	var r = baseFilename(f);
	// cut off extension (for reviews)
	if( /.*\..*\./g.test(r) )
		r = r.substr(0, r.lastIndexOf("."));
    r = (r.length > filename_max) ? r.substr(0, filename_max) + '...' : r;
	return r;
}

function generateTextBox(tmpFilenames, realFilenames) {
	// initialize globals: FIXME
	filenames = tmpFilenames.split("<sep>");
    realfilenames = realFilenames.split("<sep>");
    filename_max = 35;
	conTEXTheight = 300;
	searchSite = "";
    topMargin = 25;

	var div = make('div');
	div.setAttribute('id','conTEXT_content');

	var pre = make('div');
	div.appendChild(pre);

	var iframe = make('iframe');
	iframe.setAttribute('id','conTEXT_iframe');
	iframe.setAttribute('width','100%');
//	iframe.setAttribute('height',conTEXTheight);
	iframe.setAttribute('scrolling','no');
	iframe.setAttribute('border','0');
	iframe.setAttribute('style','border:0px; margin-top:' + topMargin + 'px;');
	div.appendChild(iframe);
    return div;
}
