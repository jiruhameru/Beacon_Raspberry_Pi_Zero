import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gtk, Gdk, GdkPixbuf
from gi.repository import GLib

import cairo
import random
import math
import numpy as np

from matplotlib.backends.backend_gtk3agg import (
    FigureCanvasGTK3Agg as FigureCanvas)

from matplotlib.figure import Figure
import matplotlib.pyplot as plt



class Figure_plot_Canvas(FigureCanvasGTK3Agg):
     def __init__(self): #, parent, scoreArea
        super(Figure_plot_Canvas, self).__init__()
        pass
        #self.parent = parent
        #self.scoreArea = scoreArea
        #self.f = fig #Figure(figsize=(8, 4), dpi=100)
        #self.a = self.f.add_subplots(111)
        #self.step = self.parent.step
        #self.x = self.parent.x
        #self.y = self.parent.y
        #self.mpl_connect("draw_event", self.on_plot)
      
     def on_plot(self, event):
        self.y = np.append(self.y, [self.scoreArea.total_score])
        self.step += 1
        self.x = np.append(self.x, [self.step])
        colors = ['black']*len(self.x)

        segments = self.find_contiguous_colors(colors)
        start= 0
        for seg in segments:
           end = start + len(seg)
           self.a.clear()
           self.a.plot(self.x[start:end],self.y[start:end],lw=2,c=seg[0])
           start = end

