## Amarok Reader ############
*Script for Amarok 2*  
Displays text or html files found in the playing directory and (optionally) web reviews for the currently playing album.

This is basically my Amarok 1.4 script [conTEXT](http://kde-apps.org/content/show.php?content=40231) ported to Amarok 2.
Now it will open a separate window as it is still impossible for scripts to insert something into the context view in Amarok 2. Which is one of the reasons for the new name :) I will have a look what can be done to achieve better integration in the future...

By default the window will open automatically when you start Amarok. This can be turned off in the Settings menu. Also you can close and re-open it anytime and even assign it a shortcut in Settings > Configure Shortcuts. If you use kwin as a window manager (KDE default), you can easily make the window remember its size and position: Right-click title bar > More Actions > Special Window Settings...

The script tries to read the font and color set in KDE config, so it should roughly match your desktop appearance. If it does not work for you, please report and I will try to fix it.

Old reviews downloaded by conTEXT in Amarok 1.4 should mostly still work.

**System requirements**: Amarok >= 2.6, Python 2.x, Linux. Other OSs are untested but might work; Amarok 2.5 does NOT work. If you have .nfo files with ascii art, consider installing the font Lucida ConsoleP.

**Usage**: The icon in the upper left corner will open the review search menu. Here you can click a site name to start a single search, select sites for auto-search on album change, or manually start a search on all sites. Found reviews are stored in the playing directory. The menu includes two buttons for opening the current file externally and for moving it to trash.

**Navigation**: Use the left/right buttons or mouse wheel on the header bar to switch between multiple files. Hover over the up/down arrows to scroll comfortably. Left-click to speed up. Right-click to jump a page up/down. Click the little bar to jump to top/bottom.

### Changelog ##################
v1.0 2013.06.29  
First release for Amarok 2. Changes since the last conTEXT release:
* now opens a separate window
* minor UI improvements:
  + use mouse wheel on header bar to switch between files
  + slightly prettier design, added some hover effects, colored feedback in search menu,...
* problems with special characters in directory names probably fixed
* major overhaul of site searches
* added amazon.com
* removed features:
  + currently no configuration options except "Autostart"
  + removed punkbands.com, it is dead

#### Ideas for future improvements ###############
* retrieve urls in parallel, should make it a bit faster
* increase search hits by being more tolerant with terms like The, and, I, II, III etc.
* intelligent caching of files for non-album dirs and streams
* show id3 comment as a file?
* allow user to modify search params (artist, album)?
* auto-update site parsers when broken
