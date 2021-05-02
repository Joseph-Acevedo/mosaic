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

    IMAGE_WIDTH = 600
    IMAGE_HEIGHT = 450

    FREE_IMG = 0

    # weights for the tinge, original percent, glass percent
    IMG_TINGE_WEIGHTS = (0.2, 0.8)

    def __init__(self):
        # plt.ion()
        # plt.rcParams['toolbar'] = 'None'

        self.curr_width = 3
        self.curr_height = 3

        # define max dimensions of the image
        self.img_imgs = np.full( (self.MAX_IMAGES_WIDE, self.MAX_IMAGES_TALL, 100, 100, 3), 127, np.uint8)
        self.free_imgs = np.zeros((self.MAX_IMAGES_TALL, self.MAX_IMAGES_WIDE))
        self.n_free_imgs = self.curr_width + self.curr_height - 1

        self.stream = cv2.VideoCapture(0)

        if not self.stream.isOpened():
            print("[ERROR] Couldn't open video stream, quitting")
            exit() 

        self.load_questions()
        self.camera_loop()

    def load_questions(self):
        lines = []
        with open("questions.txt", encoding="utf8") as f:
            lines = f.readlines()
        self.questions = {question: False for question in lines}
        self.set_unasked_question()

    def set_unasked_question(self):
        keys = self.questions.keys()
        unasked = [q for q in keys if not self.questions[q]]
        if len(unasked) == 0:
            print("Out of questions! Exiting!")
            exit()
        else:
            self.curr_question = unasked[int(random.random() * len(unasked))]
            self.questions[self.curr_question] = True

    def submit_answer(self, text):
        self.text_box.text = ""
        self.curr_width += 1
        self.curr_height += 1
        self.n_free_imgs += self.curr_width + self.curr_height - 1
        self.set_unasked_question()

        img_locs = self.generate_img_locs(int(self.n_free_imgs - (self.curr_width*self.curr_height) / 2))
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
        # fig1, ax1 = plt.subplots(figsize=(self.FIG_WIDTH_IN, self.FIG_HEIGHT_IN))

        # fig1.subplots_adjust(bottom=0.2)
        # ax1.axis('off')
        # fig1.canvas.set_window_title(self.PROJECT_NAME)

        # t = np.arange(-2.0, 2.0, 0.001)

        # axbox = fig1.add_axes([0.1, 0.05, 0.8, 0.075])
        # self.text_box = TextBox(axbox, "")
        # self.text_box.on_submit(self.submit_answer)

        rval, frame = self.stream.read()
        self.user_text = ""
        # axim1 = ax1.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        # question = plt.figtext(0.5, 0.15, self.curr_question, ha="center", fontsize=12)
        frame_count = 0
        while rval:
            rval, frame = self.stream.read()

            frame = self.process_frame(frame)
            cv2.imshow(self.PROJECT_NAME, frame)
            if self.process_key_event(cv2.waitKey(1)) == -1:
                break

            if frame_count % 100 == 0:
                self.set_unasked_question()

            frame_count += 1
            # question.set_text(self.curr_question)
            # axim1.set_data(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            # fig1.canvas.flush_events()
        self.stream.release()
        cv2.destroyAllWindows()

    def process_key_event(self, key):
        # Take least significant byte
        key = key & 0xFF
        ESC, CR, LF = 27, 13, 10
        if key == ESC or key == 'q':
            return -1
        elif key == CR or key == LF:
            pass
        else:
            pass

        
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
        
        concatted_frame = cv2.resize(cv2.vconcat([cv2.hconcat(list_h)
                        for list_h in tinged_imgs]), (self.IMAGE_WIDTH, self.IMAGE_HEIGHT))
                    
        concatted_frame = cv2.copyMakeBorder(concatted_frame, 20, 100, 20, 20, cv2.BORDER_CONSTANT)
        
        text_width, text_height = cv2.getTextSize(self.curr_question, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
        img = cv2.putText(concatted_frame,
                          self.curr_question, 
                          (int(self.IMAGE_WIDTH / 2 - text_width / 2) , self.IMAGE_HEIGHT + text_height + 30),
                          cv2.FONT_HERSHEY_SIMPLEX,
                          0.5,
                          (255, 255, 255),
                          2)
        
        img = cv2.rectangle(img, 
                            (20, self.IMAGE_HEIGHT + text_height + 50), 
                            (self.IMAGE_WIDTH + 20, self.IMAGE_HEIGHT + 100), 
                            (255, 255, 255), 
                            1)

        return img#cv2.resize(concatted_frame, (self.curr_width, self.curr_height))

    def tinge_img(self, img, rgb):
        # rgb must be a 3-tuple
        glass = np.full(img.shape, rgb, np.uint8)
        return cv2.addWeighted(img, self.IMG_TINGE_WEIGHTS[0], glass, self.IMG_TINGE_WEIGHTS[1], 0)


if __name__ == "__main__":
    Mosaic()