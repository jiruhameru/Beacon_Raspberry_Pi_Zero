import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gtk, Gdk, GdkPixbuf
from gi.repository import GLib

import cairo
import random
import math

class NeighborsImageArea(Gtk.DrawingArea):

     def __init__(self, parent, w, h, beacon):
        super(NeighborsImageArea, self).__init__()
        self.parent = parent
        self.w = w
        self.h = h
        self.beacon = beacon
        self.set_hexpand(True)
        self.set_vexpand(True)
        self.set_halign(Gtk.Align.FILL)
        self.set_valign(Gtk.Align.FILL)
        self.connect('draw', self.on_draw)

        screen = self.get_screen()

     #def on_draw(self, widget, cr, *args):
     def on_draw(self, widget, event):
        cr = widget.get_property('window').cairo_create()# ++
        height = widget.get_allocated_height()
        width = widget.get_allocated_width()

        if (self.parent.strategy == 1):
            red = 0
            blue = 1
        else:
            red = 1
            blue = 0

        cr.set_source_rgb(red, 0.0, blue)
        cr.rectangle(0, 0, width, height)
        cr.fill()


        cr.translate(width/2, height/2) # move to the center
        cr.set_source_rgba(1,1,1,1.0)
        cr.arc(0, 0, width/2, 0, 2*math.pi) #draw white circle
        cr.fill()

        cr.set_source_rgba(0,0,0,1.0)
        cr.set_line_width(4.5)
        cr.arc(0, 0, width/4, 0, 2*math.pi) #draw white circle
        cr.stroke()

        radius = width/2 - (width*0.05)
        radius4 = width/4 - (width*0.05)
        number_of_neighbors = len(self.beacon.devices_dictionary)
        #draw neighbors in proximity
        #for i in range(number_of_neighbors+1):
        for i in range(len(self.beacon.neighbors)):
            while True:
                ids = list(self.beacon.devices_dictionary.keys())

                # x = random.uniform(-radius, radius)
                # y = random.uniform(-radius, radius)
                # if math.sqrt(x ** 2 + y ** 2) < radius:
                #     break

                if(self.beacon.devices_dictionary[ids[i]][1]) >= -65:
                    x = random.uniform(-radius4, radius4)
                    y = random.uniform(-radius4, radius4)
                    if math.sqrt(x ** 2 + y ** 2) < radius4:
                        break
                else:
                    x = random.uniform(-radius, radius)
                    y = random.uniform(-radius, radius)
                    if math.sqrt(x ** 2 + y ** 2) < radius:
                        break
            #if self.beacon.devices_dictionary[i][0] == 1:
            # ids = list(self.beacon.devices_dictionary.keys())
            if(self.beacon.devices_dictionary[ids[i]][1]) >= -75:
                if int(self.beacon.devices_dictionary[ids[i]][0]) == 1:
                    red = 0
                    blue = 1
                else:
                    red = 1
                    blue = 0
                cr.set_source_rgba(red, 0, blue, 1.0)
                cr.arc(x, y, width*0.05, 0, 2*math.pi)
                cr.stroke_preserve()
                cr.fill()

        cr.set_source_rgb(0.0, 0.0, 0.0)
        cr.select_font_face("Impact", cairo.FONT_SLANT_NORMAL,
        cairo.FONT_WEIGHT_BOLD)
