import threading
import cv2
import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox
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

        self.curr_width = 1
        self.curr_height = 1

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
        print(text)
        self.text_box.text = ""
        self.curr_width += 1
        self.curr_height += 1
        self.curr_question = self.questions[int(random.random() * len(self.questions))]
        
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
        return cv2.resize(frame, (self.curr_width, self.curr_height))

if __name__ == "__main__":
    Mosaic()