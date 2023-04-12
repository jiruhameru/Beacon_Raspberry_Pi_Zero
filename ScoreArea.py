import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gtk, Gdk, GdkPixbuf
from gi.repository import GLib

import cairo
import random
import numpy as np
import math

class ScoreArea(Gtk.DrawingArea):
     MAX_NUMBER_OF_BARS = 10

     min_score = 0
     max_score = 1
     initial_draw = True
     def __init__(self, parent, score, total_score):
        super(ScoreArea, self).__init__()
        self.parent = parent
        self.score = score
        self.total_score = total_score
        self.set_hexpand(True)
        self.set_vexpand(True)
        self.set_halign(Gtk.Align.FILL)
        self.set_valign(Gtk.Align.FILL)
        self.connect('draw', self.on_draw)

        screen = self.get_screen()


     def on_draw(self, widget, cr, *args):
        #cr = widget.get_property('window').cairo_create() #++
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

        cr.set_source_rgb(1.0, 1.0, 1.0) #font black
        cr.select_font_face("Impact", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        #cr.move_to(width*0.10, height*0.40) ##on Raspi
        cr.move_to(width/12, height*.5)
        cr.set_font_size(90) ##on Raspi
        #cr.show_text( "Score: "+ str(self.total_score) )
        cr.show_text( str(self.total_score) )
        # self.total_score = round( self.total_score + self.parent.score )        

     def on_draw_old(self, widget, cr, *args):
        height = widget.get_allocated_height()
        width = widget.get_allocated_width()
        width_of_bars = round(width/11) #max. number of nars = [0,10]

        if self.max_score == 1: #first run
            number_of_bars = int(round( abs(self.score*self.MAX_NUMBER_OF_BARS)/10 )) + 1
        elif self.max_score == 0:
            number_of_bars = 1
        elif self.score >= 0:
            #number_of_bars = int(round( abs(self.score*self.MAX_NUMBER_OF_BARS/self.max_score) )) + 1
            # number of bars + offset
            number_of_bars = int(round( abs(self.score*self.MAX_NUMBER_OF_BARS/self.max_score) )) + int(round( abs(self.min_score*self.MAX_NUMBER_OF_BARS/self.max_score) ))
        else:
            #number_of_bars = self.MAX_NUMBER_OF_BARS - int(round( abs(self.score*self.MAX_NUMBER_OF_BARS/self.min_score) )) + 1
            #number_of_bars = 1
            #number_of_bars = int( abs(self.score-self.min_score)*self.MAX_NUMBER_OF_BARS ) + 1
            number_of_bars = int( abs(self.score-self.min_score)*self.MAX_NUMBER_OF_BARS ) + 1

        cr.set_source_rgb(0.0, 0.0, 0.0)
        #print(number_of_bars)
        print(number_of_bars, " BARS. SCORE: ", self.score, ", MIN: ", self.min_score, " ,  MAX: ", self.max_score)

        for i in range(1, number_of_bars+1):
            cr.rectangle(width-(width_of_bars*i), 0, width_of_bars/2, height-10)
            cr.fill()

     def set_min_score(self, min):
         self.min_score = min

     def set_max_score(self, max):
         self.max_score = max
