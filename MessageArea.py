import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gtk, Gdk, GdkPixbuf
from gi.repository import GLib

import cairo
import random
import numpy as np
import math

class MessageArea(Gtk.DrawingArea):
     def __init__(self, message):
        super(MessageArea, self).__init__()
        self.message = message
        self.set_hexpand(True)
        self.set_vexpand(True)
        self.set_halign(Gtk.Align.FILL)
        self.set_valign(Gtk.Align.FILL)
        self.connect('draw', self.on_draw)

        screen = self.get_screen()


     def on_draw(self, widget, cr, *args):
        height = widget.get_allocated_height()
        width = widget.get_allocated_width()

        cr.set_source_rgb(1.0, 1.0, 1.0)
        cr.rectangle(0, 0, width, height)
        cr.fill()
        cr.move_to(0, height/2)
        cr.select_font_face("Impact", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(100)
        cr.set_source_rgb(0.0, 0.0, 0.0)
        cr.show_text( self.message )

     def set_message(self, message):
        self.message = message
