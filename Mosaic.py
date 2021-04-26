import threading
import cv2
import numpy as np
import matplotlib.pyplot as plt
from ImageRequest import ImageRequest
from matplotlib.widgets import TextBox

class Mosaic:

    PROJECT_NAME = "You, a Mosaic of Concepts"

    FIG_HEIGHT_IN = 8
    FIG_WIDTH_IN = 10

    IMAGES_WIDE = 120
    IMAGES_TALL = 80

    def __init__(self):
        plt.ion()
        plt.rcParams['toolbar'] = 'None'

        self.image_thread = ImageRequest()
        self.stream = cv2.VideoCapture(0)

        if not self.stream.isOpened():
            print("[ERROR] Couldn't open video stream, quitting")
            exit()    
        
        self.camera_loop()

    def camera_loop(self):

        fig1, ax1 = plt.subplots(figsize=(self.FIG_WIDTH_IN, self.FIG_HEIGHT_IN))

        ax1.axis('off')
        fig1.canvas.set_window_title(self.PROJECT_NAME)

        rval, frame = self.stream.read()
        axim1 = ax1.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        while rval:
            rval, frame = self.stream.read()

            frame = self.process_frame(frame)
            
            axim1.set_data(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            fig1.canvas.flush_events()
        
    def process_frame(self, frame):
        return cv2.resize(frame, (self.IMAGES_WIDE, self.IMAGES_TALL))

if __name__ == "__main__":
    Mosaic()