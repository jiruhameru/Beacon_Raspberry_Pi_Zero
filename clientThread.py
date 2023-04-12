import socket               # Import socket module
import time
import threading
import sys
import numpy as np


class clientThread (threading.Thread):
   def __init__(self, beacon_gui, sock, id, data):
      threading.Thread.__init__(self)
      self.beacon_gui = beacon_gui
      self._running = True
      self.sock = sock
      self.id = id
      self.data = data
      self.cum_scores =  np.array([0])

   def run(self):
       while True:
           try:
               self.sock.send(self.id.to_bytes(2, 'big'))
               #print(self.sock.recv(1024), "---------------")
               #while(self.sock.recv(1024) != b'N'):
               if(self.sock.recv(1024) == b'Y'):
                   print("logging data....", self.beacon_gui.experiment_paused, ', ', self.beacon_gui.experiment_launched, ', ', self.beacon_gui.launched_once)
                   self.beacon_gui.experiment_launched = True
                   if self.beacon_gui.experiment_paused == True:
                       self.beacon_gui.launched_once = True
                       self.beacon_gui.experiment_paused = False #$
                       self.beacon_gui.paused_once = False
                       self.beacon_gui.scoreArea.total_score = 0

                   self.sock.send(self.data.encode('utf-8'))
               else:
                   if (b'N' in self.sock.recv(1024)):
                       #print("STOPPING-----------------")
                       self.beacon_gui.experiment_paused = True

                       #self.beacon_gui.scoreArea.total_score = 0
                       self.beacon_gui.score = 0
                       self.beacon_gui.cum_score = 0
                       self.beacon_gui.step = 1
                       self.beacon_gui.x = np.array([1])
                       self.beacon_gui.y = np.array([0])
                       #self.beacon_gui.f_slot.clf();

                       # self.beacon_gui.f_slot.get_tk_widget().pack_forget() #+
                       # self.beacon_gui.f.get_tk_widget().pack_forget()    #+
                       # try:
                       #     self.beacon_gui.figCanvas.wierdobject.get_tk_widget().pack_forget()
                       # except AttributeError:
                       #     pass

                       # self.beacon_gui.f.clf()
                       # self.beacon_gui.f = Figure(figsize=(8, 4), dpi=100)
                       # self.beacon_gui.figCanvas = FigureCanvas(self.beacon_gui.f)
                       #self.beacon_gui.a.clear()
                       #self.beacon_gui.a_slot.clear()



                       #self.beacon_gui.f.clf()
                       #self.beacon_gui.a = self.f.add_subplot(111) #X
                       #self.beacon_gui.a_slot = self.f_slot.add_subplot(111)

                       self.beacon_gui.neighbors = set()
                       self.beacon_gui.scores = np.array([0])
                       self.beacon_gui.cum_scores = np.array([0])
                       self.beacon_gui.devices_dictionary = {}

                   #self.sock.send(str(max(self.cum_scores)).encode('utf-8'))
                   #self.sock.send(max(self.cum_scores).encode('utf-8'))
                   self.sock.send(b'')
                   #print('data logging is disabled')
           except:
               #print("Disconnected from server")
               pass
               #s = socket.socket()
               #self.connected = False

          #send_data(self.sock, self.id, self.data)

   def terminate(self):
       print("TERMINATING THREAD")
       self._running = False
       #self.connected = False

   def set_log_data(self, data):
       self.data = data

# def send_data(s, id, data):
#     s.send(id.to_bytes(2, 'big'))
#     #while x < 50:
#     print("Sending data . . . . . . . . . . . . . .")
#     time.sleep(1)
#     s.send(data.encode('utf-8'))
#
#     time.sleep(1)
#     s.send(b'')
#     s.close                     # Close the socket when done
