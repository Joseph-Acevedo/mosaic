import threading
import cv2
import random
import numpy as np
from time import sleep

import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox

from ImageRequester import get_images

class Mosaic:

    PROJECT_NAME = "You, a Mosaic of Concepts"

    FIG_HEIGHT_IN = 8
    FIG_WIDTH_IN = 10

    MAX_IMAGES_WIDE = 240
    MAX_IMAGES_TALL = 160

    FREE_IMG = 0

    # weights for the tinge, original percent, glass percent
    IMG_TINGE_WEIGHTS = (0.2, 0.8)

    def __init__(self):
        plt.ion()
        plt.rcParams['toolbar'] = 'None'

        self.curr_width = 1
        self.curr_height = 1

        # define max dimensions of the image
        self.img_imgs = np.full( (self.MAX_IMAGES_WIDE, self.MAX_IMAGES_TALL, 100, 100, 3), 127, np.uint8)
        # self.img_imgs = [[np.full((100, 100, 3), (127, 127, 127), np.uint8)] * self.MAX_IMAGES_WIDE] * self.MAX_IMAGES_TALL
        print(f"img_imgs is {self.img_imgs.shape}")
        self.free_imgs = np.zeros((self.MAX_IMAGES_TALL, self.MAX_IMAGES_WIDE))
        self.n_free_imgs = self.curr_width + self.curr_height - 1

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
        self.n_free_imgs += self.curr_width + self.curr_height - 1
        self.curr_question = self.questions[int(random.random() * len(self.questions))]

        img_locs = self.generate_img_locs(int(self.n_free_imgs / 2))
        get_images(text, self.img_imgs, img_locs)
        
    def generate_img_locs(self, n_imgs):
        locs = []
        row, col = 0, 0
        for i in range(n_imgs):
            if self.n_free_imgs <= 0:
                return locs
            while (self.free_imgs[row,col] != self.FREE_IMG):
                col = int(self.curr_width  * random.random())
                row = int(self.curr_height * random.random())
            locs.append( (row,col) )
            self.free_imgs[row][col] += 1
            self.n_free_imgs -= 1
        return locs

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
            # print(f"total: {self.curr_width * self.curr_height}\tfree: {self.n_free_imgs}")
            rval, frame = self.stream.read()

            frame = self.process_frame(frame)
            
            question.set_text(self.curr_question)
            axim1.set_data(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            fig1.canvas.flush_events()
        
    def process_frame(self, frame):
        tinged_imgs = [ ]
        frame = cv2.resize(frame, (self.curr_width, self.curr_height))
        for row in range(self.curr_width):
            row_imgs = []
            for col in range(self.curr_height):
                tinge_color = frame[row, col]
                tinged_img = self.tinge_img(self.img_imgs[row, col], tinge_color)
                row_imgs.append(tinged_img)
            tinged_imgs.append(row_imgs)
        
        concatted_frame = cv2.vconcat([cv2.hconcat(list_h)
                        for list_h in tinged_imgs])

        return concatted_frame#cv2.resize(concatted_frame, (self.curr_width, self.curr_height))

    def tinge_img(self, img, rgb):
        # rgb must be a 3-tuple
        glass = np.full(img.shape, rgb, np.uint8)
        return cv2.addWeighted(img, self.IMG_TINGE_WEIGHTS[0], glass, self.IMG_TINGE_WEIGHTS[1], 0)


if __name__ == "__main__":
    Mosaic()