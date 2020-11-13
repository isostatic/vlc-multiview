#! /usr/bin/python

#
# gtk example/widget for VLC Python bindings
# Copyright (C) 2009-2010 the VideoLAN team
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston MA 02110-1301, USA.
#

"""VLC Gtk Widget classes + example application.

This module provides two helper classes, to ease the embedding of a
VLC component inside a pygtk application.

VLCWidget is a simple VLC widget.

DecoratedVLCWidget provides simple player controls.

When called as an application, it behaves as a video player.

$Id$
"""

import gtk
gtk.gdk.threads_init()

import sys
import vlc
import time
import math
import re
import netifaces

from gettext import gettext as _

# Create a single vlc.Instance() to be shared by (possible) multiple players.
instance = vlc.Instance()

class VLCWidget(gtk.DrawingArea):
    """Simple VLC widget.

    Its player can be controlled through the 'player' attribute, which
    is a vlc.MediaPlayer() instance.
    """
    def toggle_mute(self):
        if (self.player.audio_get_mute() == 1):
            print "Unmute at vol",self.player.audio_get_volume()
            self.unmute()
        else:
            print "Mute at vol",self.player.audio_get_volume()
            self.mute()

    def toggle_volume(self, amount):
        origvol = self.player.audio_get_volume();
        newvol = origvol+amount
        if (newvol < 0):
            newvol = 0
        self.set_lbl("Volume: " + str(newvol))
        self.player.audio_set_volume(newvol);

    def onscroll (self, widget, event):
        if (event.direction == gtk.gdk.SCROLL_UP):
            self.toggle_volume(10)
        if (event.direction == gtk.gdk.SCROLL_DOWN):
            self.toggle_volume(-10)

    def onclick (self, widget, event):
        if (event.button == 1):
            self.toggle_mute()
        if (event.button == 2):
            self.toggle_volume(-20)
        if (event.button == 3):
            self.toggle_volume(10)
        print "Event button ", event.button

    def mute (self):
        self.player.audio_set_mute(1)
        self.modify_bg(gtk.STATE_NORMAL, None)
        self.set_lbl("")

    def unmute (self):
        self.player.audio_set_mute(0)
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse('red'))
        vol = self.player.audio_get_volume();
        self.set_lbl("Volume: " + str(vol))

    def __init__(self, *p):
        gtk.DrawingArea.__init__(self)
        self.player = instance.media_player_new()
        def handle_embed(*args):
            if sys.platform == 'win32':
                self.player.set_hwnd(self.window.handle)
            else:
                self.player.set_xwindow(self.window.xid)
            return True
        self.connect("map", handle_embed)
        self.mute()
        self.set_size_request(320, 200)
        self.set_events(self.get_events() | gtk.gdk.BUTTON_PRESS_MASK )
        self.connect('button-press-event', self.onclick)
        self.connect('scroll-event', self.onscroll)

    def set_lbl_data(self, _l, _n):
        self._orig_name = _n
        self._lbl = _l

    def set_lbl(self, new_text):
        try:
            if (new_text == ""):
                self._lbl.set_text(self._orig_name)
            else :
                self._lbl.set_text(self._orig_name + " (" + new_text + ")")
        except:
            print "Not initiatied yet"

class DecoratedVLCWidget(gtk.VBox):
    """Decorated VLC widget.

    VLC widget decorated with a player control toolbar.

    Its player can be controlled through the 'player' attribute, which
    is a Player instance.
    """
    def __init__(self, *p):
        gtk.VBox.__init__(self)
        self._vlc_widget = VLCWidget(*p)
        self.player = self._vlc_widget.player
        self.pack_start(self._vlc_widget, expand=True)
        self._label = self.get_player_info_label()
        self.pack_start(self._label, expand=False)

    def get_player_info_label(self):
        lbl = gtk.Label()
        lbl.set_text("Loading");
        return lbl

    def set_lbl_data(self, _lbl, _name):
        self._vlc_widget.set_lbl_data(_lbl, _name)

class DecoratedVLCWidgetEBox(gtk.EventBox):

    def set_file(self, lbl, flbl, fname):
        self.vlcbox._label.set_text(flbl);
        self.vlcbox.set_lbl_data(self.vlcbox._label, flbl)
        self.frame.set_label(lbl);
        self.vlcbox.player.set_media(instance.media_new(fname))

    def __init__(self, *p):
        gtk.EventBox.__init__(self)
        self.vlcbox = DecoratedVLCWidget()
        self.frame = gtk.Frame()
        self.frame.add(self.vlcbox)
        self.add(self.frame)


#class StatusFooter(gtk.HBox):
#    def get_footer_label(self):
#        lbl = gtk.Label()
#        lbl.set_size_request(920, 200)
#        lbl.set_text("Multiviewer");
#        return lbl
#    def get_quit_button(self, mvp):
#        btn = gtk.Button()
#        btn.set_label("Quit");
#        btn.set_size_request(32, 200)
#        btn.connect("clicked", mvp.quit)
#        return btn
#    def __init__(self, _parent):
#        self._parent = _parent
#        gtk.HBox.__init__(self)
#        self.lbl = self.get_footer_label()
#        self.add(self.lbl)
#        self.add(self.get_quit_button(self._parent))
    
class StatusFooter(gtk.Frame):
    def get_ip_address(self):
        ips = "";
        for iface in netifaces.interfaces():
            try:
                ip = netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['addr']
                if ip == "127.0.0.1":
                    continue
                ips = ips + ip + ","
            except:
                pass
        return ips[:-1]

    def quit(self,event):
        gtk.main_quit
        quit()
    def edit(self,event):
        v = ConfigWindow()
        v.show()

    def __init__(self, *p):
        gtk.Frame.__init__(self)
        self.box = gtk.HBox(spacing=6)
        self.ip = gtk.Label()
        self.ip.set_text("IP: " + self.get_ip_address())

        self.add(self.box)

        self.editbutton = gtk.Button(label="Sources (ctrl-s)")
        self.editbutton.connect("clicked", self.edit)

        self.restartbtn = gtk.Button(label="Restart (ctrl-x)")
        self.restartbtn.connect("clicked", self.quit)

        self.box.pack_start(self.editbutton, False, True, 10)
        self.box.pack_start(self.ip, True, True, 0)
        self.box.pack_start(self.restartbtn, False, True, 10)
        
class ConfigWindow(gtk.Window):
    def quit(self,event):
        # save
        start_iter = self.textbuffer.get_start_iter()
        end_iter = self.textbuffer.get_end_iter()
        new_content = self.textbuffer.get_text(start_iter, end_iter, True)
        try:
            conffile = open("config", "w")
            conffile.write(new_content)
        except:
            pass

        gtk.main_quit
        quit()
    def cancel(self,event):
        self.destroy()
    def handle_key(self, widget, event):
        if event.keyval == 65307:
            # escape
            self.cancel(event);
            
        if event.state & gtk.gdk.CONTROL_MASK:
            if gtk.gdk.keyval_name(event.keyval).lower() == "x":
                self.quit(event)

    def __init__(self, *p):
        gtk.Window.__init__(self)
        self.set_title("Edit config")

        self.txt = gtk.TextView()
        self.textbuffer = self.txt.get_buffer()
        try:
            conf = open("config").read()
            self.textbuffer.set_text(conf)
        except:
            pass

        self.box = gtk.HBox(spacing=6)
        self.cancelbtn = gtk.Button(label="Cancel (esc)")
        self.restartbtn = gtk.Button(label="Save + Restart (ctrl-x)")
        self.restartbtn.connect("clicked", self.quit)
        self.cancelbtn.connect("clicked", self.cancel)

        self.box.pack_start(self.cancelbtn, False, False, 2)
        self.box.pack_end(self.restartbtn, False, False, 2)

        self.cont = gtk.VBox()
        self.cont.pack_start(self.txt, True, True, 2)
        self.cont.pack_end(self.box, False, False, 2)
        self.add(self.cont)

        self.connect("key-release-event", self.handle_key)

        self.fullscreen()
        self.show_all()
    

class MultiVideoPlayer:
    """Example multi-video player.

    It plays multiple files side-by-side, with per-view and global controls.
    """

    def quit(self,event):
        gtk.main_quit
        quit()

    def toggle_mute(self, widget, fnum):
        if fnum < len(self._allPlayers):
            self._allPlayers[fnum].vlcbox._vlc_widget.toggle_mute()

    def handle_key(self, widget, event):
        if event.state & gtk.gdk.CONTROL_MASK:
            if gtk.gdk.keyval_name(event.keyval).lower() == "x":
                self.quit(event)
            if gtk.gdk.keyval_name(event.keyval).lower() == "s":
                self.lblBox.edit(event)
        if event.keyval > 47 and event.keyval < 58:
            fnum = event.keyval-48
            self.toggle_mute(self,fnum)
        if event.keyval > 64 and event.keyval < 92:
            fnum = event.keyval-55
            self.toggle_mute(self,fnum)
        if event.keyval > 96 and event.keyval < 124:
            fnum = event.keyval-87
            self.toggle_mute(self,fnum)

    def realize_cb(self, widget):
        cursor = gtk.gdk.Cursor(gtk.gdk.CursorType.WATCH)
        widget.window.set_cursor(cursor)

    def main(self, filenames):
        # Build main window
        self._allPlayers = []
        maxCols = int(math.ceil(math.sqrt(len(filenames))))
        window=gtk.Window()
        window.set_title("Multiviewer")
        mainbox=gtk.VBox()
        cur_col=0
        cur_row=0
        filenamenum = 0
        for _row in range(0, maxCols):
            _thisrow=gtk.HBox()
            for _col in range(0, maxCols):
                if filenamenum >= len(filenames):
                    blank = gtk.HBox()
                    blank.set_size_request(320, 200)
                    _thisrow.add(blank)
                    continue
                fname = filenames[filenamenum]
                letter = str(filenamenum)
                if filenamenum > 9:
                        letter = str(chr(filenamenum+55))
                vf = DecoratedVLCWidgetEBox()
                flbl = re.sub(r'.*#', '', fname)
                fname = re.sub(r' *#.*', '', fname)
                print "Setting fname to",fname
                print "Setting flbl to",flbl
                vf.set_file(letter, flbl, fname)
                _thisrow.add(vf)
                self._allPlayers.append(vf)
                filenamenum+=1
            mainbox.add(_thisrow)


        self.lblBox = StatusFooter()

        wbox = gtk.VBox()
        wbox.pack_start(mainbox, True, True, 2)
        wbox.pack_end(self.lblBox, False, False, 2)

        mainbox.set_size_request(300, 1000)
        wbox.set_size_request(300, 60)
        window.add(wbox)


        for v in self._allPlayers:
            v.vlcbox.player.play();

        window.show_all()
        window.fullscreen()
        window.connect("key-release-event", self.handle_key)
        window.connect("destroy", self.quit)
        window.connect("realize", self.realize_cb)
        gtk.main()

if __name__ == '__main__':
    sources = "";
    try:
        with open("config") as f:
            sources = f.readlines()
    except:
        pass
    sources = [x.strip() for x in sources]
    sources = filter(None, sources)
    p=MultiVideoPlayer()
    p.main(sources)

