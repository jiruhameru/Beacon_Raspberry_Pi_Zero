import time
import threading
import sys
import numpy as np

class Graph_update(threading.Thread):
     def __init__(self, figCanvas):
        threading.Thread.__init__(self)
        self.figCanvas = figCanvas

     def run(self):
        self.figCanvas.draw()

