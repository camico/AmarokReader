try {
    var argFiles = "%s";
    var argRealFiles = "%s";
    var argLastFile = "%s";
    var argScrollPos = "%s";
    var argSearchSites = "%s";
    var exBox = get('conTEXT_box');
    if (exBox != null)
        exBox.parentNode.removeChild(exBox);

    var box = make('div');
    box.setAttribute('id','conTEXT_box');
    var header = make('div');
    header.setAttribute('class', 'header');
    header.setAttribute('onmousewheel', 'wheelOnHeader(event)');
    var headerTitle = make('span');
    var headerFile = make('div');
    headerFile.setAttribute('id', 'conTEXT_file');
    headerFile.setAttribute('class', 'header-file');
    headerFile.appendChild(text(''));
    headerTitle.appendChild(headerFile);
    var headerNext = make('a');
    headerNext.setAttribute('id', 'conTEXT_next');
    headerNext.setAttribute('onclick', 'showNext()');
    headerNext.setAttribute('class', 'header-next');
    headerNext.setAttribute('title', 'Switch to next file');
    headerTitle.appendChild(headerNext);
    var headerPrev = make('a');
    headerPrev.setAttribute('id','conTEXT_prev');
    headerPrev.setAttribute('onclick','showPrev()');
    headerPrev.setAttribute('class', 'header-prev');
    headerPrev.setAttribute('title', 'Switch to previous file');
    headerTitle.appendChild(headerPrev);
    header.appendChild(headerTitle);
    var actualBox = generateTextBox(argFiles, argRealFiles);
    box.appendChild(header);
    box.appendChild(actualBox);
    get("body").appendChild(box);

    showFileWithName(argLastFile);
    info(filenames.length);

    searchSites = argSearchSites;
    conTEXTscrollpos = argScrollPos;
    conTEXTscrollremember = true;

    if (filenames.length == 1) {
        get('conTEXT_next').style.visibility = "hidden";
        get('conTEXT_prev').style.visibility = "hidden";
    }

} catch (e) {
    alert('An error occurred in Amarok Reader when updating its content. ' +
        'Please report this to the developer:\n\n' + e);
}
