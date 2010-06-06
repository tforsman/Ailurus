#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
# Ailurus - make Linux easier to use
#
# Copyright (C) 2007-2010, Trusted Digital Technology Laboratory, Shanghai Jiao Tong University, China.
# Copyright (C) 2009-2010, Ailurus Developers Team
#
# Ailurus is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Ailurus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ailurus; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA

from __future__ import with_statement
import gtk, pango
from lib import *
from libu import *

class GConfCheckButton(gtk.CheckButton):
    def __toggled(self, w):
        value = self.get_active()
        import gconf
        g = gconf.client_get_default()
        g.set_bool(self.key, value)
    def __init__(self, text, key, tooltip = None):
        gtk.CheckButton.__init__(self)
        self.key = key
        self.set_label(text)
        if not tooltip: tooltip = _('GConf key: ')+key
        else: tooltip += _('\nGConf key: ')+key
        self.set_tooltip_markup(tooltip)
        import gconf
        g = gconf.client_get_default()
        self.set_active( g.get_bool(key) )
        self.connect('toggled', self.__toggled)

class GConfComboBox(gtk.HBox):
    def __init__(self, key, values_shown, values_gconf, tooltip = None):
        gtk.HBox.__init__(self, False, 10)
        
        self.key = key
        self.values_gconf = values_gconf
        
        combo = gtk.combo_box_new_text()
        if not tooltip: tooltip = _('GConf key: ')+key
        else: tooltip += _('\nGConf key: ')+key
        combo.set_tooltip_text(tooltip)
        for s in values_shown:
            combo.append_text(s)
        import gconf
        g = gconf.client_get_default()
        value = g.get_string(key)
        for i, s in enumerate(values_gconf):
            if s==value:
                combo.set_active(i)
                break
        combo.connect('changed', self.__option_changed)
        combo.connect('scroll-event', lambda *w:True)
        self.pack_start(combo, False, False)
    def __option_changed(self, combo):
        value = self.values_gconf[ combo.get_active() ]
        import gconf
        g = gconf.client_get_default()
        g.set_string(self.key, value)

class GConfTextEntry(gtk.HBox):
    def __value_changed(self, *w): 
        self.button.set_sensitive(True)
        
    def __button_clicked(self, *w):
        value = self.entry.get_text()
        import gconf
        g = gconf.client_get_default()
        g.set_string(self.key, value)
        self.button.set_sensitive(False)
    
    def __init__(self, key):
        self.key = key
        self.entry = gtk.Entry()    
        import gconf
        g = gconf.client_get_default()
        value = g.get_string(key)
        if value: self.entry.set_text(value) 
        
        self.button = gtk.Button(stock=gtk.STOCK_APPLY)
        self.button.set_sensitive(False)
        self.entry.connect('changed', self.__value_changed)
        self.button.connect('clicked', self.__button_clicked)
        
        tooltip_text = _('GConf key: ') + key
        self.entry.set_tooltip_text(tooltip_text)
        self.button.set_tooltip_text(tooltip_text)
        
        gtk.HBox.__init__(self, False, 5)
        self.pack_start(self.entry, False)
        self.pack_start(self.button, False)

class GConfShortcutKeyEntry(gtk.HBox):
    def grab_key(self, *w):
        import support.keygrabber
        window = support.keygrabber.GrabberWindow ()
        window.main ()
        self.shortcut_entry.set_text(window.shortcut)

    def __entry_value_changed(self, *w):
        import gconf
        g = gconf.client_get_default()
        g.set_string('/apps/metacity/keybinding_commands/' + self.number, self.command_entry.get_text())
        g.set_string('/apps/metacity/global_keybindings/run_' + self.number, self.shortcut_entry.get_text())

    def __clear_entry_content(self, *w):        
        self.command_entry.set_text('')
        self.shortcut_entry.set_text('')
        
    def __init__(self, number):
        is_string_not_empty(number)
        gtk.HBox.__init__(self, False)
        
        import gconf
        g = gconf.client_get_default()

        self.number = number
        self.command_entry = gtk.Entry()
        self.command_entry.set_tooltip_text(
            _('The command which will be run.') + _('\nGConf key: ') + '/apps/metacity/keybinding_commands/' + self.number)
        value = g.get_string('/apps/metacity/keybinding_commands/'+number)
        if value: self.command_entry.set_text(value)
        self.command_entry.connect('changed', self.__entry_value_changed)

        self.shortcut_entry = gtk.Entry()
        self.shortcut_entry.set_tooltip_text(
            _('The shortcut key.') + _('\nGConf key: ') + '/apps/metacity/global_keybindings/run_' + self.number)
        self.shortcut_entry.connect('grab-focus', self.grab_key)
        value = g.get_string('/apps/metacity/global_keybindings/run_'+number)
        if value: self.shortcut_entry.set_text(value)
        self.shortcut_entry.connect('changed', self.__entry_value_changed)
        
        self.clear_entry_content_button = gtk.Button(stock = gtk.STOCK_CLEAR)
        self.clear_entry_content_button.connect('clicked', self.__clear_entry_content)

        self.pack_start(self.command_entry, True)
        self.pack_start(self.shortcut_entry, False)
        self.pack_start(self.clear_entry_content_button, False)

class ImageChooser(gtk.Button):
    import gobject
    __gsignals__ = {'changed':( gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_STRING,) ) }
    
    def get_image_filter(self):
        filter = gtk.FileFilter()
        filter.set_name(_("Images"))
        for type, pattern in [('image/png', '*.png'),
                              ('image/jpeg', '*.jpg'),
                              ('image/gif', '*.gif'),
                              ('image/x-xpixmap', '*.xpm'),
                              ('image/x-svg', '*.svg'),]:
            filter.add_mime_type(type)  
            filter.add_pattern(pattern)
        return filter
    
    def choose_image(self, *args):
        title = _('Choose an image')
        chooser = gtk.FileChooserDialog(title, None, gtk.FILE_CHOOSER_ACTION_OPEN,
                (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                 gtk.STOCK_OPEN, gtk.RESPONSE_OK)
                )
        import os
        chooser.set_current_folder('/usr/share/pixmaps/')
        chooser.set_select_multiple(False)
        chooser.add_filter(self.get_image_filter())
        if chooser.run() == gtk.RESPONSE_OK:
            image_path = chooser.get_filename()
            self.emit('changed', image_path)
            self.display_image(image_path)
        chooser.destroy()
    
    def display_image(self, image_path):
        child = self.get_child()
        if child:
            self.remove(child)
        
        pixbuf = gtk.gdk.pixbuf_new_from_file(image_path)
        pixbuf = self.scale_pixbuf(pixbuf)
        image = gtk.image_new_from_pixbuf(pixbuf)
        self.add(image)
        self.show_all()

    def scale_pixbuf(self, pixbuf):
        pixbuf_height = pixbuf.get_height()
        pixbuf_width = pixbuf.get_width()
        if self.image_max_height != -1 and pixbuf_height > self.image_max_height:
            scale = float(pixbuf_height)/float(self.image_max_height)
            new_height = self.image_max_height
            new_width = pixbuf_width/scale
        elif self.image_max_width != -1 and pixbuf_width > self.image_max_width:
            scale = float(pixbuf_width)/float(self.image_max_width)
            new_width = self.image_max_width
            new_height = pixbuf_height/scale
        else:
            return pixbuf
        return pixbuf.scale_simple(int(new_width), int(new_height), gtk.gdk.INTERP_HYPER)

    def __init__(self, tooltip_text = '', image_max_width = -1, image_max_height = -1):
        is_string_not_empty(tooltip_text)
        assert isinstance(image_max_width, int)
        assert isinstance(image_max_height, int)
        
        gtk.Button.__init__(self)
        if tooltip_text: self.set_tooltip_text(tooltip_text)
        self.image_max_width = image_max_width
        self.image_max_height = image_max_height

        self.connect('clicked', self.choose_image)

    @classmethod
    def scale_image(cls, old_path, new_path, new_width, new_height):
        pixbuf = gtk.gdk.pixbuf_new_from_file(old_path)
        if pixbuf.get_width == new_width and pixbuf.get_height == new_height:
            pass
        else:
            pixbuf = pixbuf.scale_simple(new_width, new_height, gtk.gdk.INTERP_HYPER)
        pixbuf.save(new_path, 'png')

class GConfNumericEntry(gtk.HBox):
    def __value_changed(self, *w):
        self.button_apply.set_sensitive(True)
    def __apply(self, *w):
        value = self.spin.get_value_as_int()
        import gconf
        g = gconf.client_get_default()
        g.set_int(self.key, value)
        self.button_apply.set_sensitive(False)
    def __init__(self, key, min, max, tooltip=''):
        self.key = key
        
        if tooltip: tooltip+='\n'
        tooltip += _('GConf key: ')+key
        tooltip += _('\nMinimum value: %(min)s. Maximum value: %(max)s.')%{'min':min, 'max':max}
        
        self.spin = spin = gtk.SpinButton()
        spin.set_size_request(100, -1)
        spin.set_range(min, max)
        spin.set_increments(1, 1)
        spin.set_update_policy(gtk.UPDATE_ALWAYS)
        spin.set_numeric(True)
        spin.set_tooltip_text(tooltip)
        spin.set_wrap(False)
        spin.set_snap_to_ticks(True)
        import gconf
        g = gconf.client_get_default()
        value = g.get_int(key)
        spin.set_value(value)
        spin.connect('value-changed', self.__value_changed)
        spin.connect('scroll-event', lambda *w:True)

        self.button_apply = button_apply = gtk.Button( _('Apply') )
        button_apply.set_sensitive(False)
        button_apply.connect('clicked', self.__apply)
        
        gtk.HBox.__init__(self, False, 5)
        self.pack_start(spin, False)
        self.pack_start(button_apply, False)

class GConfHScale(gtk.HScale):
    def __init__(self, gconf_key, min, max, tooltip = ''):
        self.gconf_key = gconf_key
        
        if tooltip: tooltip += '\n'
        tooltip += _('GConf key: ') + gconf_key
        
        gtk.HScale.__init__(self)
        self.set_value_pos(gtk.POS_RIGHT)
        self.set_digits(0)
        self.set_range(min, max)
        import gconf
        g = gconf.client_get_default()
        value = g.get_int(self.gconf_key)
        self.set_value(value)
        self.connect("value-changed", self.__value_changed)
        if tooltip: self.set_tooltip_text(tooltip)
        
    def __value_changed(self, *w):
        new_value = int( self.get_value() )
        import gconf
        g = gconf.client_get_default()
        g.set_int(self.gconf_key, new_value)
        
class Setting(gtk.VBox):
    def __title(self, text):
        label = gtk.Label()
        label.set_markup('<b>%s</b>'%text)
        return left_align(label)

    def __init__(self, box, title, category):
        assert isinstance(box, gtk.Container)
        assert isinstance(title, (str, unicode) )
        assert isinstance(category, list)
        assert category != []
        for i in category: 
            assert isinstance(i, str)

        gtk.VBox.__init__(self, False, 0)
        self.set_border_width(5)
        self.pack_start( self.__title(title), False )
        self.pack_start( box, False)
        box.set_border_width(5)
        
        self.category = category

class FirefoxPrefText(gtk.Label):
    def __init__(self, text, key):
        assert isinstance(text, (str, unicode)) and text
        assert isinstance(key, str) and key
        new_text = '%s <small>(%s)</small>' % (text, key)
        gtk.Label.__init__(self)
        self.set_markup(new_text)
        self.set_ellipsize(pango.ELLIPSIZE_END)
        self.set_alignment(0, 0.5)

class FirefoxBooleanPref(gtk.HBox):
    def __init__(self, key):
        assert isinstance(key, str) and key
        self.key = key
        self.combo = combo = gtk.combo_box_new_text()
        combo.append_text(_('Yes'))
        combo.append_text(_('No'))
        combo.connect('scroll-event', lambda w: True)
        gtk.HBox.__init__(self, False, 5)
        self.pack_start(combo, False)
        self.get_value()
        combo.connect('changed', lambda w: self.set_value())
    def get_value(self):
        try:
            value = bool(firefox.get_pref(self.key))
        except:
            pass
        else:
            self.combo.set_active({True:0, False:1}[value])
    def set_value(self):
        index = self.combo.get_active()
        if index == -1: firefox.remove_pref(self.key)
        else: firefox.set_pref(self.key, {0:True, 1:False}[index])

class FirefoxNumericPref(gtk.SpinButton):
    def __init__(self, key, min, max, step, default_value):
        assert isinstance(key, str) and key
        assert isinstance(min, (int, long))
        assert isinstance(max, (int, long))
        assert isinstance(step, (int, long)) and step>0
        assert isinstance(default_value, (int, long)) and min<=default_value<=max
        self.key = key
        self.default_value = default_value
        gtk.SpinButton.__init__(self)
        self.set_range(min, max)
        self.set_increments(step, step)
        self.set_update_policy(gtk.UPDATE_IF_VALID)
        self.set_numeric(True)
        self.set_wrap(False)
        self.set_snap_to_ticks(True) # if True invalid values should be corrected.
        self.m_get_value()
        self.connect('value-changed', lambda w: self.m_set_value())
    def m_get_value(self):
        try:
            value = int(firefox.get_pref(self.key))
        except:
            self.set_value(self.default_value)
        else:
            self.set_value(value)
    def m_set_value(self):
        value = self.get_value_as_int()
        firefox.set_pref(self.key, value)

class FirefoxConfig(gtk.CheckButton):          
    def check_active(self):
        import os
        if not os.path.isfile(self.path + 'user.js'):
            return False
        else :
            with open(self.path + 'user.js') as f:
                p = self.config_item.split('\n')
                v = f.readlines()
                for s in p:
                    for i in v:
                        if i[:-1] == s:
                            return True
                return False

    def __init__(self, container, config_item, 
             plain_text, tooltip=None, ):
        self.path = firefox.preference_dir
        gtk.CheckButton.__init__(self)
        assert isinstance(container, gtk.Container)
        self.__container = container
        assert isinstance(config_item, str)
        self.config_item = config_item
        assert isinstance(plain_text, (str,unicode))
        self.plain_text = plain_text
        self.label = gtk.Label(plain_text)
        self.add(self.label)
        self.tooltip = tooltip
        self.set_active(self.check_active())
        self.connect("query-tooltip", lambda *w: True)

if __name__ == '__main__':
    table = gtk.Table()
    table.attach(FirefoxPrefText('content.interrupt.parsing' , 'content.interrupt.parsing'), 
                 0, 1, 0, 1)
    table.attach(FirefoxBooleanPref('content.interrupt.parsing'),
                 1, 2, 0, 1, gtk.FILL)
    table.attach(FirefoxPrefText('content.maxtextrun', 'content.maxtextrun'),
                 0, 1, 1, 2)
    table.attach(FirefoxNumericPref('content.maxtextrun', 0, 8192, 1024, 1024),
                 1, 2, 1, 2, gtk.FILL)
    window = gtk.Window()
    window.set_position(gtk.WIN_POS_CENTER)
    window.connect('delete-event', gtk.main_quit)
    window.add(table)
    window.show_all()
    window.set_size_request(300, -1)
    gtk.main()
    print firefox.get_pref('content.interrupt.parsing')
    print firefox.get_pref('content.maxtextrun')