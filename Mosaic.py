import threading
import cv2
import random
import numpy as np
from time import sleep

import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox
from ImageRequest import ImageRequest
from matplotlib.widgets import TextBox

class Mosaic:

    PROJECT_NAME = "You, a Mosaic of Concepts"

    FIG_HEIGHT_IN = 8
    FIG_WIDTH_IN = 10

    MAX_IMAGES_WIDE = 240
    MAX_IMAGES_TALL = 160

    # weights for the tinge, original percent, glass percent
    IMG_TINGE_WEIGHTS = (0.4, 0.6)

    def __init__(self):
        plt.ion()
        plt.rcParams['toolbar'] = 'None'

        self.curr_width = 1
        self.curr_height = 1

        # define max dimensions of the image
        self.img_imgs = [[np.full((100, 100, 3), (0,0,255), np.uint8)] * self.MAX_IMAGES_WIDE] * self.MAX_IMAGES_TALL

        self.image_thread = ImageRequest()
        self.stream = cv2.VideoCapture(0)

        if not self.stream.isOpened():
            print("[ERROR] Couldn't open video stream, quitting")
            exit() 

        self.load_questions()
        self.camera_loop()

    def load_questions(self):
        self.questions = []
        with open("questions.txt", encoding="utf8") as f:
            self.questions = f.readlines()

        self.curr_question = self.questions[int(random.random() * len(self.questions))]
        print(self.curr_question)


    def submit_answer(self, text):
        self.text_box.text = ""
        self.curr_width += 1
        self.curr_height += 1
        self.curr_question = self.questions[int(random.random() * len(self.questions))]
        sleep(0.2)
        
        
    def camera_loop(self):
        fig1, ax1 = plt.subplots(figsize=(self.FIG_WIDTH_IN, self.FIG_HEIGHT_IN))

        fig1.subplots_adjust(bottom=0.2)
        ax1.axis('off')
        fig1.canvas.set_window_title(self.PROJECT_NAME)

        t = np.arange(-2.0, 2.0, 0.001)

        axbox = fig1.add_axes([0.1, 0.05, 0.8, 0.075])
        self.text_box = TextBox(axbox, "")
        self.text_box.on_submit(self.submit_answer)

        rval, frame = self.stream.read()
        axim1 = ax1.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        question = plt.figtext(0.5, 0.15, self.curr_question, ha="center", fontsize=12)
        while rval:
            rval, frame = self.stream.read()

            frame = self.process_frame(frame)
            
            question.set_text(self.curr_question)
            axim1.set_data(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            fig1.canvas.flush_events()
        
    def process_frame(self, frame):
        for x in range(self.curr_width):
            for y in range(self.curr_height):
                continue

        return cv2.resize(frame, (self.MAX_IMAGES_WIDE, self.MAX_IMAGES_TALL))

    def tinge_img(self, img, rgb):
        # rgb must be a 3-tuple
        glass = np.full(img.shape, rgb, np.uint8)
        return cv2.addWeighted(img, self.IMG_TINGE_WEIGHTS[0], glass, self.IMG_TINGE_WEIGHTS[1], 0)


if __name__ == "__main__":
    Mosaic()