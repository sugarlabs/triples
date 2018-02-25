# activity.py
# my standard link between sugar and my activity
"""
    Copyright (C) 2011  Peter Hewitt
    Copyright (C) 2013  Ignacio Rodriguez

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

"""

from gettext import gettext as _
import logging

from gi.repository import Gtk
from gi.repository import Gdk
import pygame

from sugar3.activity import activity
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity.widgets import ActivityToolbarButton
from sugar3.activity.widgets import StopButton
from sugar3.graphics.toolbutton import ToolButton
from sugar3.graphics.style import GRID_CELL_SIZE
from sugar3 import profile

import sugargame.canvas
import load_save
import Triples


class PeterActivity(activity.Activity):
    def __init__(self, handle):
        super(PeterActivity, self).__init__(handle)

        # Get user's Sugar colors
        sugarcolors = profile.get_color().to_string().split(',')
        colors = [[int(sugarcolors[0][1:3], 16),
                   int(sugarcolors[0][3:5], 16),
                   int(sugarcolors[0][5:7], 16)],
                  [int(sugarcolors[1][1:3], 16),
                   int(sugarcolors[1][3:5], 16),
                   int(sugarcolors[1][5:7], 16)]]

        # No sharing
        self.max_participants = 1

        # Build the activity toolbar.
        toolbox = ToolbarBox()

        activity_button = ActivityToolbarButton(self)
        toolbox.toolbar.insert(activity_button, 0)
        activity_button.show()

        cyan = ToolButton('cyan')
        toolbox.toolbar.insert(cyan, -1)
        cyan.set_tooltip(_('Restart'))
        cyan.connect('clicked', self._button_cb, 'new')
        cyan.show()

        separator = Gtk.SeparatorToolItem()
        separator.props.draw = True
        toolbox.toolbar.insert(separator, -1)
        separator.show()

        label = Gtk.Label()
        label.set_use_markup(True)
        label.show()
        labelitem = Gtk.ToolItem()
        labelitem.add(label)
        toolbox.toolbar.insert(labelitem, -1)
        labelitem.show()

        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        toolbox.toolbar.insert(separator, -1)
        separator.show()

        stop = StopButton(self)
        toolbox.toolbar.insert(stop, -1)
        stop.show()

        toolbox.show()
        self.set_toolbar_box(toolbox)

        # Create the game instance.
        self.game = Triples.Triples(colors, sugar=True)

        # Build the Pygame canvas.
        self._pygamecanvas = sugargame.canvas.PygameCanvas(self)
        # Note that set_canvas implicitly calls
        # read_file when resuming from the Journal.
        self.set_canvas(self._pygamecanvas)
        self.game.canvas = self._pygamecanvas
        self.game.set_label(label)

        Gdk.Screen.get_default().connect('size-changed',
                                             self.__configure_cb)

        # Start the game running.
        self._pygamecanvas.run_pygame(self.game.run)

    def get_preview(self):
        return self._pygamecanvas.get_preview()

    def __configure_cb(self, event):
        ''' Screen size has changed '''
        logging.debug(self._pygamecanvas.get_allocation())
        pygame.display.set_mode((Gdk.Screen.width(),
                                 Gdk.Screen.height() - GRID_CELL_SIZE),
                                pygame.RESIZABLE)

        self.game.run(restore=True)

    def _button_cb(self, button=None, color=None):
        self.game.do_button(color)

    def read_file(self, file_path):
        try:
            f = open(file_path, 'r')
        except Exception as e:
            logging.error("Couldn't open %s: %s" % (file_path, e))
            return
        load_save.load(f)
        f.close()

    def write_file(self, file_path):
        f = open(file_path, 'w')
        load_save.save(f)
        f.close()
