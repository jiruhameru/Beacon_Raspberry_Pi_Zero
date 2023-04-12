#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import sys
import asyncio
import argparse
import re
import aioblescan
from aioblescan.plugins import EddyStone
from aioblescan.aioblescan import *

import subprocess

from random import *

from time import sleep
from threading import Thread, Timer, Event
import threading

from datetime import datetime
import time
import datetime as dt
import math
import random
import csv

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from gi.repository import Gtk, Gdk, GdkPixbuf
from gi.repository import GLib
Gdk.threads_init()
import cairo
from gi.repository.Gdk import Screen

import RPi.GPIO as GPIO #raspi
GPIO.setmode(GPIO.BOARD) #raspi

from matplotlib.backends.backend_gtk3agg import (
    FigureCanvasGTK3Agg as FigureCanvas)

from matplotlib.figure import Figure
import matplotlib.pyplot as plt


from NeighborsImageArea import NeighborsImageArea
from ScoreArea import ScoreArea
from MessageArea import MessageArea
#from Canvas_plot import Canvas_plot
from Graph_update import Graph_update

from clientThread import clientThread
import os

import numpy as np

from gi.repository import GObject as gobject

#import keyboard

class Beacon_GUI:
    original = sys.stdout
    REWARD = 1.0
    TEMP = 1.8
    SUCK = -1.4
    PUNISH = -1.0

    def destroy(self, widget, data=None):
        Gtk.main_quit()

    def __init__(self, id_beacon, strategy, opts):
        self.status = 1

        self.socket_device = socket.socket()         # Create a socket object
        self.connected = False #False
        # self.connect_to_server(self.socket_device, "192.168.7.1", 10016)

        self.showNeighbors = True
        self.resetting = False

        self.start_interaction = False
        #creating new beacon..
        self.id_beacon = id_beacon
        self.strategy = strategy
        self.score = 0
        self.cum_score = 0
        self.rssi = None
        self.std = 0 #+++
        self.neighbors = set()
        self.devices_dictionary = {}
        #test sample: {1:[1, -45], 2:[1, -30], 3:[0, -35], 4:[0, -60], 5:[1, -80]}
        self.scores = np.array([0])
        self.cum_scores = np.array([0])
        self.opts = opts

        self.experiment_launched = True #False
        self.launched_once = True
        self.experiment_paused = False
        self.paused_once = False

        self.session_num = 1

        #setting up window
        self.window = Gtk.Window()
        #self.window.set_name('default_screen')
        screenvar = Screen.get_default()
        self.w = screenvar.get_width()
        self.h = screenvar.get_height()
        self.window.set_size_request(self.w, self.h)
        self.window.set_gravity(Gdk.Gravity.NORTH_EAST)
        self.window.set_direction(Gtk.TextDirection.RTL)


        self.window.set_position(Gtk.WindowPosition.CENTER)
        self.window.fullscreen()
        #self.window.set_keep_above(True)

        #drawing area
        self.darea = Gtk.DrawingArea()
        self.darea.set_hexpand(True)
        self.darea.set_vexpand(True)
        #self.darea.set_halign(Gtk.Align.FILL)
        #self.darea.set_valign(Gtk.Align.FILL)

        self.grid = Gtk.Grid()
        self.main_widget = Gtk.VBox()
        self.main_widget.add(self.grid)
        #self.window.add(self.main_widget)

        self.messageArea = MessageArea("Please wait")
        self.message_widget = Gtk.VBox()
        self.message_widget.add(self.messageArea)
        self.window.add(self.message_widget)

        #self.window.add(grid)

        self.neighborsArea = NeighborsImageArea(self, self.w/4, self.h/3, self)


        css_data = """
        #default_screen{
            background: green;
        }
        #coop_screen{
            background: blue;
        }
        #defect_screen{
            background: red;
        }
        """

        self._css_provider = Gtk.CssProvider()
        #css = open("change-window-background.css", 'rb')
        #self._css = css.read()
        #css.close()
        #self._css_from = bytes("{0}".encode("utf-8"))
        #self._css_provider.load_from_data(self._css.replace(self._css_from, bytes("green".encode("utf-8"))))
        self._css_provider.load_from_data(css_data.encode())
        self.context = Gtk.StyleContext()
        screen = Gdk.Screen.get_default()
        self.context.add_provider_for_screen(screen, self._css_provider,
                                   Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)



        self.grid.add(self.neighborsArea)
        self.grid.attach_next_to(self.darea, self.neighborsArea, Gtk.PositionType.LEFT, 3, 1)
        self.scoreArea = ScoreArea ( self, 0,0 ) #first iteration -> score;total_score = 0
        self.grid.attach_next_to(self.scoreArea, self.darea, Gtk.PositionType.BOTTOM, 2, 1) #4, 1

        self.f = Figure(figsize=(8, 4), dpi=100)
        self.f_slot = Figure(figsize=(8, 4), dpi=100)
        self.a = self.f.add_subplot(111)
        self.a_slot = self.f_slot.add_subplot(111)
        self.step = 1
        self.x = np.array([1])
        self.y = np.array([0])
        #np.array([np.random.random(1)])
        self.figCanvas = FigureCanvas(self.f)
        self.figCanvas_slot = FigureCanvas(self.f_slot)
        self.figCanvas.mpl_connect("draw_event", self.on_plot)
        self.figCanvas_slot.mpl_connect("draw_event", self.on_plot_slot)
        self.grid.attach_next_to(self.figCanvas, self.scoreArea, Gtk.PositionType.RIGHT, 2, 1)
        #self.grid.attach_next_to(self.figCanvas_slot, self.figCanvas, Gtk.PositionType.RIGHT, 1, 1)


        self.darea.connect('draw', self.update_window)  #self.update_screen_text, self.update_window
        ##self.neighborsArea.connect('draw', self.neighborsArea.on_draw)
        ##self.scoreArea.connect('draw', self.scoreArea.on_draw)

        # self.window.connect("key_press_event",self.on_key_pressed) #PC
        self.joy = 33
        # self.joyUp = 31
        # self.joyDown = 35
        # self.joyLeft = 29
        # self.joyRight = 37
        self.key1 = 40
        # self.key2 = 38
        self.key3 = 36
        #
        GPIO.setup(self.joy, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        #GPIO.setup(self.joyUp, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        #GPIO.setup(self.joyDown, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        #GPIO.setup(self.joyLeft, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        #GPIO.setup(self.joyRight, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        GPIO.setup(self.key1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.key3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        #
        # gobject.threads_init()
        GPIO.add_event_detect(self.joy, GPIO.RISING, callback=self.on_key_pressed)
        # GPIO.add_event_detect(self.joy, GPIO.RISING, callback=self.th_key_pressed)
        GPIO.add_event_detect(self.key1, GPIO.RISING, callback=self.set_invisible_display)
        GPIO.add_event_detect(self.key3, GPIO.RISING, callback=self.reset_app)
        GPIO.setwarnings(False)

        #if (self.strategy == 1):
            #self.window.set_name('coop_screen')
        #    self.window.modify_bg(Gtk.StateFlags.NORMAL, Gdk.Color(0, 0, 65535)) #65535
        #else:
            #self.window.set_name('defect_screen')
        #    self.window.modify_bg(Gtk.StateFlags.NORMAL, Gdk.Color(65535, 0, 0)) #65535


        self.window.connect("destroy", Gtk.main_quit)
        self.window.show_all()

    def th_key_pressed(self, channel):
        k = threading.Thread(target=self.run_joy_thread, args=(channel, ))
        k.start()

    def run_joy_thread(self, channel):
        # print("TESTING KEY PRESS EVENT")
        self.strategy = abs(self.strategy-1) #on raspi
        self.advertise()

    def relaunch(self):
        #subprocess.call(['sh', './relaunch.sh'])
        subprocess.call('lxterminal --command="sh ./relaunch.sh"', cwd='/root/Beacon', shell=True)

    def kill_app(self):
        self.window.destroy()
        self.resetting = True

    def connect_to_server(self, socket,  host, port):
        if(not self.connected):
            try:
                socket.connect((host, port))
                self.connected = True
                self.experiment_launched = True
                print("Connected to server")
            except:
                #print("Re-connecting to server..")
                time.sleep(1)

    def on_plot(self, event):#(name, canvas, renderer)
            #print("PLotting..")
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

    def on_plot_slot(self, event):#(name, canvas, renderer)
            self.y = np.append(self.y, [self.scoreArea.total_score])
            self.step += 1
            self.x = np.append(self.x, [self.step])
            colors = ['black']*len(self.x)

            segments = self.find_contiguous_colors(colors)
            start= 0
            #self.a_slot.set_xlim([-10, -100])
            if len(self.x)>5:
                self.a_slot.set_xlim([ self.x[-5] , self.x[-1]])
                #self.a_slot.set_ylim([ self.y[-5] , self.y[-1]])
                start= self.x[-5]

            for seg in segments:
                end = start + len(seg)
                self.a_slot.clear()
                self.a_slot.plot(self.x[start:end],self.y[start:end],lw=2,c=seg[0])
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

# ========================================================================================================================

    def on_key_pressed(self, channel): #raspi
        self.strategy = abs(self.strategy-1) #on raspi
        self.advertise()

    def set_invisible_display(self, channel):
        if(self.showNeighbors):
            self.grid.remove(self.neighborsArea)
            self.grid.remove(self.figCanvas)
            self.grid.attach_next_to(self.figCanvas, self.scoreArea, Gtk.PositionType.RIGHT, 1, 1)
            self.showNeighbors = False
        else:
            self.grid.add(self.neighborsArea)
            self.grid.remove(self.figCanvas)
            self.grid.attach_next_to(self.figCanvas, self.scoreArea, Gtk.PositionType.RIGHT, 2, 1)
            self.showNeighbors = True

    def reset_app(self, channel):
        Thread(target = self.relaunch).start()
        Thread(target = self.kill_app).start()

        # f = open('/mnt/sda3/devzoneII/python/RASPI_222/Beacon_u/sessions/_log_'+str(self.session_num)+'_.csv','a')
        f = open('/root/Beacon/sessions/_log_'+str(self.session_num)+'_.csv','a')
        f.write('---------------------------------------------------------------------------------------- \n')
        f.flush()

# ========================================================================================================================


    def on_key_pressed_(self, widget, event): #PC keyboard
    # def on_key_pressed(self, channeL): #raspi
        if event.keyval==97: #key A
            print("JOY PRESSED ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| ", self.strategy)
            self.strategy = abs(self.strategy-1) #on raspi
            self.advertise()
        if event.keyval==98:
            if(self.showNeighbors):
                self.grid.remove(self.neighborsArea)
                self.grid.remove(self.figCanvas)
                self.grid.attach_next_to(self.figCanvas, self.scoreArea, Gtk.PositionType.RIGHT, 1, 1)
                self.showNeighbors = False
            else:
                self.grid.add(self.neighborsArea)
                self.grid.remove(self.figCanvas)
                self.grid.attach_next_to(self.figCanvas, self.scoreArea, Gtk.PositionType.RIGHT, 2, 1)
                self.showNeighbors = True
        if event.keyval==120:
            # print("Restarting program..")
            # subprocess.call(['sh', './relaunch.sh'])
            # self.window.destroy()
            # self.resetting = True

            Thread(target = self.relaunch).start()
            Thread(target = self.kill_app).start()

            #f = open('/mnt/sda3/devzoneII/python/RASPI_222/Beacon_u/sessions/_log_'+str(self.session_num)+'_.csv','a')
            #print("wrting to /mnt/sda3/devzoneII/python/RASPI_222/Beacon_u/sessions/_log_"+str(self.session_num)+"_.csv")
            #f.write('---------------------------------------------------------------------------------------- \n')
            #f.flush()
            #
            # os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)
            # sys.exit()



    def scan_devices(self, e):
        mysocket = aioblescan.create_bt_socket(self.opts.device)
        fac=e._create_connection_transport(mysocket,aioblescan.BLEScanRequester,None,None)
        conn,btctrl = e.run_until_complete(fac) # aioblescan.aioblescan.BLEScanRequester
        btctrl.process=self.my_process
        btctrl.send_scan_request()
        try:
            e.run_forever()
        except KeyboardInterrupt:
            print('keyboard interrupt')
        finally:
            # closing event loop
            btctrl.stop_scan_request()
            conn.close()
            e.close()

    def exitfunc(self):
        #print("Exit Time", datetime.now())
        #sys.stdout = self.original
        #os.system("shutdown now -h")
        os._exit(0)#exit program

    #def update_window(self, widget, event, *args):

    def update_window(self, da, ctx, *args):
        #ctx = widget.get_property('window').cairo_create() #++
        #if(self.GPIO.input(self.joy) == 0)
        #if GPIO.input(self.joy)==0 or GPIO.input(self.joyUp)==0 or GPIO.input(self.joyDown)==0 or GPIO.input(self.joyLeft)==0 or GPIO.input(self.joyRight)==0:
            #self.strategy = abs(self.strategy-1) #on raspi
            #print("STRATEGY CHANGED ~~~~ ", self.strategy)

        if (self.strategy == 1):
            red = 0
            blue = 1
            #self.window.modify_bg(Gtk.StateFlags.NORMAL, Gdk.Color(0, 0, 65535)) #65535
            #color_str = "blue"
            #self.window.set_name('coop_screen')

        else:
            red = 1
            blue = 0
            #self.window.modify_bg(Gtk.StateFlags.NORMAL, Gdk.Color(65535, 0, 0)) #65535
            #color_str = "red"
            #self.window.set_name('defect_screen')


        #self._css_provider.load_from_data(self._css.replace(self._css_from, bytes(color_str.encode("utf-8"))))
        #self.context = Gtk.StyleContext()


        height = da.get_allocated_height()
        width = da.get_allocated_width()

        ctx.set_source_rgb(red, 0.0, blue)
        ctx.rectangle(0, 0, width, height)
        ctx.fill()

        #ctx.set_source_rgb(0.0, 0.0, 0.0) #font black
        #ctx.select_font_face("Impact", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        #ctx.move_to(width*0.10, height*0.40) ##on Raspi
        #ctx.set_font_size(85) ##on Raspi

        # self.scoreArea.total_score = round( self.scoreArea.total_score + self.score, 2 )
        #ctx.show_text( "Score: "+ str(self.scoreArea.total_score) )

    def refresh(self):
        print(self.connected)
        #add this to take into account the startegy change key press
        self.darea.queue_draw()
        self.scoreArea.queue_draw()
        self.neighborsArea.queue_draw()

        ts = time.mktime( dt.datetime.today().timetuple() )
        #print(ts, ",   ", (ts %30))
        if((ts % 10) == 0):
            plot_1_thread = Graph_update(self.figCanvas)
            plot_2_thread = Graph_update(self.figCanvas_slot)
            plot_1_thread.start()
            plot_1_thread.join()

            #plot_2_thread.start()
            #plot_2_thread.join()
        #    self.figCanvas.draw()
        #    self.figCanvas_slot.draw()

        #if (not self.connected):
        #    self.connect_to_server(self.socket_device, "192.168.7.1", 10016)

        if (self.experiment_launched == True and self.launched_once == True):
            #print("Adding components")
            self.window.remove(self.message_widget)
            self.window.add(self.main_widget)
            self.window.show_all()

            self.darea.queue_draw()
            self.scoreArea.queue_draw()
            self.neighborsArea.queue_draw()
            #if((ts % 10) == 0):
            #    plot_1_thread = Graph_update(self.figCanvas)
            #    plot_2_thread = Graph_update(self.figCanvas_slot)
            #    plot_1_thread.start()
            #    plot_1_thread.join()

                #plot_2_thread.start()
                #plot_2_thread.join()
            #    self.figCanvas.draw()
            #    self.figCanvas_slot.draw()
            self.launched_once = False
        elif self.experiment_paused == True and self.paused_once == False:
             #print("removing components..")
             self.window.remove(self.main_widget)
             self.messageArea.set_message("Score: "+str(round(self.scoreArea.total_score, 2)))
             self.window.add(self.message_widget)
             self.window.show_all()
             self.paused_once = True
             self.session_num = self.session_num + 1

        min_score_ = self.SUCK * len(self.devices_dictionary) #the most possible minimun score obtained given a number of neighbors
        max_score_ = self.TEMP*len(self.devices_dictionary)
        self.scoreArea.set_max_score( abs(min_score_) +  max_score_) #shifted max score on the status bar by abs(min_score_)
        self.scoreArea.set_min_score( min_score_ )
        # self.scoreArea.score = self.score
        # self.scoreArea.total_score = round (self.scoreArea.total_score + self.score, 2)

        s = None
        ts = None
        with open('/root/Beacon/sessions/sc_.txt','r') as file_sc:
            try:
                s = file_sc.read()
                self.scoreArea.score = float(s)
            except:
                print ("Value is invalid: "+str(s))


        with open('/root/Beacon/sessions/tsc_.txt','r') as file_tsc:
            try:
                ts = file_tsc.read()
                self.scoreArea.total_score = round (float(ts) + self.scoreArea.score, 2)
                print(str(self.scoreArea.total_score)+" = "+str(float(ts))+" + "+str(self.scoreArea.score))
            except:
                print ("Value is invalid: "+str(ts))

        return True

    def my_process(self, data):
        global opts

        if(self.status == 1):
            ev=aioblescan.HCI_Event()
            xx=ev.decode(data)
            f = open('/root/Beacon/sessions/_log_'+str(self.session_num)+'_.csv','a')
            #f = open('/mnt/sda3/devzoneII/python/RASPI_222/Beacon_u/sessions/_log_'+str(self.session_num)+'_.csv','a')
            if opts.eddy:
                xx=EddyStone().decode(ev)
                if xx: # print("Google Beacon {}".format(xx))
                    #print("Google Beacon {}".format(xx))
                    if self.experiment_launched:
                        #print("SAVING DATA . . . . . . . . . . . . . . . .")
                        self.rssi = xx["rssi"]
                        rssi_ = xx["rssi"]
                        instance_ = self.bytes_to_int(xx["instance"])
                        id_ = instance_[:-2] #ID of detected beacon
                        s_ = instance_[-1] # strategy of detected beacon
                        #if (rssi_ > -75):#to be changed; rssi_neigh = -75
                        self.neighbors.add( id_ )
                        self.devices_dictionary.update({id_:[s_, rssi_]}) #append strategy in a {alias:[address, strategy,..]} key-value format
                        #elif (id_ in self.neighbors):
                        #    self.neighbors.remove( id_ ) #self.neighbors.remove( self.bytes_to_int(xx["instance"]) )
                        #    try:
                        #        del self.devices_dictionary[id_]
                        #    except KeyError:
                        #        pass

                        tick_ = str( datetime.now().hour ) + ":" + str( datetime.now().minute ) + ":" + str( datetime.now().second )
                        t_sec = datetime.strptime(tick_, '%H:%M:%S').time().second

                        payoff = 0
                        b = None #rssi value
                        self.score = 0
                        estimated_distance = 0.01

                        for i in range(len(self.neighbors)):
                            if self.strategy == 1: #Cooperator
                                if(i < len(self.neighbors)):
                                    if (int(self.devices_dictionary[list(self.neighbors)[i]][0]) == 1):
                                        payoff = self.REWARD
                                        b = self.devices_dictionary[list(self.neighbors)[i]][1]
                                    elif (int(self.devices_dictionary[list(self.neighbors)[i]][0]) == 0):
                                        payoff = self.SUCK
                                        b = self.devices_dictionary[list(self.neighbors)[i]][1]
                                else:
                                    pass
                            else: #Defector
                                if(i < len(self.neighbors)):
                                    if (int(self.devices_dictionary[list(self.neighbors)[i]][0]) == 1):
                                        payoff = self.TEMP
                                        b = self.devices_dictionary[list(self.neighbors)[i]][1]
                                    elif (int(self.devices_dictionary[list(self.neighbors)[i]][0]) == 0):
                                        payoff = self.PUNISH
                                        b = self.devices_dictionary[list(self.neighbors)[i]][1]
                                else:
                                    pass

                            if(b > -65.0):	                #CATEGORY I, estimated distance: 1.0m
                                estimated_distance = 1.0
                            elif(b <= -65.0 and b > -75.0):	#CATEGORY II, estimated distance: 3.0m
                                estimated_distance = 2.0
                            # elif(b != None): #
                            #     estimated_distance = 3.0        #CATEGORY III, estimated distance: 5.0m
                            else: # b = None (i.e. no signal)
                                estimated_distance =  -1

                            if(estimated_distance == -1):
                                self.score = self.score + 0
                            else:
                                self.score = round( self.score + (payoff / estimated_distance), 2 )
                                pay_est = payoff / estimated_distance
                                print("payoff / estimated_distance: "+str(pay_est))

                            self.cum_score = self.cum_score + self.scoreArea.total_score
                            self.scores = np.append(self.scores,  [self.score])
                            self.cum_scores = np.append(self.cum_scores,  [self.scoreArea.total_score])

                        if(len(self.scores) >=2 ):
                            if(self.scores[-1] < self.scores[-2]):
                                self.std = -1 * np.std(self.scores[-2:])
                            else:
                                self.std = np.std(self.scores[-2:])

                        timestamp = time.mktime( dt.datetime.today().timetuple() )
                        my_id = int(str(self.id_beacon)[-1])

                        log_data = str(self.bytes_to_int(xx["name space"]))+";"+str(my_id)+";"+str(self.strategy)+";"+xx["mac address"]+";"+str(tick_)+";"+str(timestamp)+";"+str(self.scoreArea.total_score)+";"+str(self.score)+";"+str(len(self.neighbors))+";"+str(self.devices_dictionary)
                        f.write(log_data+str('\n'))
                        # time.sleep(1)
                        f.flush()
                        if self.connected:
                            log_thread = clientThread(self, self.socket_device, my_id, log_data) #self.id_beacon
                            log_thread.start()
                            ##self.socket_device.close()
                    else:
                        if(self.connected):
                            pass
                else:
                    pass
                    #print("None (no beacons detected)")
                if(self.resetting):
                    print("RESETTING ...")
                    sys.exit()
            else:
                ev.show(0)
            f.close()

            self.status = abs(self.status - 1)
            t_score = open('/root/Beacon/sessions/sc_.txt','w+')
            t_score.write(str(self.score))
            t_score.flush()

            tot_score = open('/root/Beacon/sessions/tsc_.txt','w+')
            tot_score.write(str(self.scoreArea.total_score))
            tot_score.flush()

        else:
            self.status = 1



    def bytes_to_int(self, bytes):
        result=""
        for i in range(len(bytes)):
            b = bytes[i]
            if(b>=0 and b<16):
                dec = b
                result += "".join(("0", str(dec)))
            elif(b>=16 and b<32):
                dec = 10 + (b-16)
                result += "".join(("", str(dec)))
            elif(b>=32 and b<48):
                dec = 20 + (b-32)
                result += "".join(("", str(dec)))
            elif(b>=48 and b<64):
                dec = 30 + (b-48)
                result += "".join(("", str(dec)))
            elif(b>=64 and b<80):
                dec = 40 + (b-64)
                result += "".join(("", str(dec)))
            elif(b>=80 and b<96):
                dec = 50 + (b-80)
                result += "".join(("", str(dec)))
            elif(b>=96 and b<112):
                dec = 60 + (b-96)
                result += "".join(("", str(dec)))
            elif(b>=112 and b<128):
                dec = 70 + (b-112)
                result += "".join(("", str(dec)))
            elif(b>=128 and b<144):
                dec = 80 + (b-128)
                result += "".join(("", str(dec)))
            else:
                dec = 90 + (b-144)
                result += "".join(("", str(dec)))

        return result

    def advertise(self):
        uid = int( str(self.id_beacon)+"0"+str(self.strategy) )
        subprocess.call(['python3', '/root/Beacon/pyBeacon/PyBeacon.py', '-i', str(uid)])
        print('Advertising..')
        #subprocess.call(['python3', '/mnt/sda3/devzoneII/python/RASPI_222/Beacon_u/pyBeacon/PyBeacon.py', '-i', str(uid)])

    def main_draw(self):
        event_loop = asyncio.get_event_loop()
        threading.Thread(target=self.scan_devices, args=(event_loop,)).start()

        GLib.timeout_add_seconds(1, self.refresh)
        #GLib.timeout_add(100, self.refresh)

        GLib.threads_init()
        Gdk.threads_init()
        Gdk.threads_enter()

        Gtk.main()
        GLib.threads_init()

    def quit_app(self):
        self.window.connect("destroy", Gtk.main_quit)

parser = argparse.ArgumentParser(description="Track BLE advertised packets")
parser.add_argument("-e", "--eddy", action='store_true', default=False,
                    help="Look specificaly for Eddystone messages.")
parser.add_argument("-a","--advertise", type= int, default=0,
                    help="Broadcast like an EddyStone Beacon. Set the interval between packet in millisec")
parser.add_argument("-u","--url", type= str, default="",
                    help="When broadcasting like an EddyStone Beacon, set the url.")
parser.add_argument("-t","--txpower", type= int, default=0,
                    help="When broadcasting like an EddyStone Beacon, set the Tx power")
parser.add_argument("-D","--device", type=int, default=0,
                    help="Select the hciX device to use (default 0, i.e. hci0).")
try:
    opts = parser.parse_args()
except Exception as e:
    parser.error("Error: " + str(e))
    sys.exit()

def main_gui():
    beacon_gui.main_draw()

#sys.stdout = open('./log.txt', 'a+')

if __name__ == "__main__":
    print('starting...')
    # beacon_gui = Beacon_GUI(111111111111111111110000000001, random.randint(0, 1), opts)
    beacon_gui = Beacon_GUI(111111111111111111110000000001, 1, opts)
    beacon_gui.advertise()
    beacon_gui.main_draw()
