#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import random

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from gi.repository import Gtk, Gdk, GdkPixbuf
from gi.repository import GLib
Gdk.threads_init()
from gi.repository.Gdk import Screen

import os
import numpy as np

from matplotlib.backends.backend_gtk3agg import (
    FigureCanvasGTK3Agg as FigureCanvas)

from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class Canvas_plot(FigureCanvas):

#    def destroy(self, widget, data=None):
#        Gtk.main_quit()

    def __init__(self, figure, a):
        self.timestep = 0.1
        self.f = figure
        self.a = self.f.add_subplot(111)

        #setting up window
        #self.window = Gtk.Window()
        #self.window.set_size_request(600, 400)

        #drawing area
        self.step = 1
        self.x = np.array([1])
        self.y = np.array([np.random.random(1)])
        #self.figCanvas = FigureCanvas(self.f)
        #self.mpl_connect("draw_event", self.on_plot)
        #self.window.add(self.figCanvas)

        #self.window.connect("destroy", Gtk.main_quit)
        #self.window.show_all()

    def on_plot(self, event):#(name, canvas, renderer)
        #print("PLotting..")
        self.y = np.append(self.y, [np.random.random(1)])
        self.step += 1
        self.x = np.append(self.x, [self.step])
        colors = ['blue']*len(self.x)

        segments = self.find_contiguous_colors(colors)
        start= 0
        for seg in segments:
            end = start + len(seg)
            self.a.plot(self.x[start:end],self.y[start:end],lw=2,c=seg[0])
            start = end

    def find_contiguous_colors(self, colors):
        # finds the continuous segments of colors and returns those segments
        segs = []
        curr_seg = []
        prev_color = ''
        for c in colors:
            if c == prev_color or prev_color == '':
                curr_seg.append(c)
            else:
                segs.append(curr_seg)
                curr_seg = []
                curr_seg.append(c)
            prev_color = c
        segs.append(curr_seg) # the final one
        return segs

    #def refresh(self):
#        self.draw()
#        return True

#    def main_draw(self):
        #GLib.timeout_add_seconds(1, self.refresh)
        #Gtk.main()

#def main_gui():
#     canvas_plot_gui.main_draw()
#
#
# if __name__ == "__main__":
#     f = Figure(figsize=(5, 4), dpi=100)
#     a = f.add_subplot(111)
#     canvas_plot_gui = Canvas_plot(f, a)
#     canvas_plot_gui.main_draw()
