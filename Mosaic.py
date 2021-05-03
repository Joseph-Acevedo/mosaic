"""
Author: Joseph Acevedo
Project: You, a Mosaic of Concepts
File: Mosaic.py
Purpose: Reads images from the default webcam and processes them to create a mosaic
    that changes resolution as questions are answered by the user, populating the
    cells of the image with images from the internet
"""

import threading
import cv2
import random
import numpy as np
from time import sleep

import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox

from ImageRequester import get_images
import Constants as const

class Mosaic:

    def __init__(self):
        self.curr_width = const.START_WIDTH
        self.curr_height = const.START_HEIGHT

        # define max dimensions of the image
        self.img_imgs = np.full( (const.MAX_IMAGES_WIDE, const.MAX_IMAGES_TALL, 100, 100, 3), 127, np.uint8)
        self.free_imgs = np.zeros((const.MAX_IMAGES_TALL, const.MAX_IMAGES_WIDE))
        self.n_free_imgs = self.curr_width + self.curr_height - 1
        self.continue_looping = True

        self.stream = cv2.VideoCapture(0)

        if not self.stream.isOpened():
            print("[ERROR] Couldn't open video stream, quitting")
            exit() 

        self.load_questions()
        self.camera_loop()

    """
    Reads the specified questions.txt file and saves a subset for use in the program. Sets the 
    first question
    """
    def load_questions(self):
        lines = []
        with open(const.QUESTIONS_FILENAME, encoding="utf8") as f:
            lines = f.readlines()

        lines = random.sample(lines, const.NUM_QUESTIONS_PER_RUN)
        self.questions = {question: False for question in lines}
        self.set_unasked_question()

    """
    Randomly chooses an unasked question from the list of questions. If there are no more questions
    to ask then it initializes the program exiting
    """
    def set_unasked_question(self):
        keys = self.questions.keys()
        unasked = [q for q in keys if not self.questions[q]]
        if len(unasked) == 0:
            self.continue_looping = False
        else:
            self.curr_question = unasked[int(random.random() * len(unasked))]
            self.questions[self.curr_question] = True
            # opecv can't display newlines so it would append an extra question mark if left on
            self.curr_question = self.curr_question.strip('\n')

    """
    Called when the user submits an answer to a question. Increases resolution of the image, requests
    new images based on their answer, and grabs a new, random, question
    """
    def submit_answer(self, text):
        self.curr_width += 1
        self.curr_height += 1
        self.n_free_imgs += self.curr_width + self.curr_height - 1
        self.set_unasked_question()

        img_locs = self.generate_img_locs(int(self.n_free_imgs - (self.curr_width * self.curr_height) / 2))
        get_images(text, self.img_imgs, img_locs)
        
    """
    Generates a list of random, unoccupied locations in the image array. If there aren't enough locations 
    in the array for the requested images will give a shorter list than expected
    """
    def generate_img_locs(self, n_imgs):
        locs = []
        row, col = 0, 0
        for i in range(n_imgs):
            if self.n_free_imgs <= 0:
                return locs
            while (self.free_imgs[row,col] != const.FREE_IMG):
                col = int(self.curr_width  * random.random())
                row = int(self.curr_height * random.random())
            locs.append( (row,col) )
            self.free_imgs[row][col] += 1
            self.n_free_imgs -= 1
        return locs

    """
    The main camera loop. Grabs frames from the camera and processes them. Once the program is exiting
    it will save the mosaic to file
    """
    def camera_loop(self):
        rval, frame = self.stream.read()
        self.user_text = ""

        while rval and self.continue_looping:
            rval, frame = self.stream.read()

            frame = self.process_frame(frame)
            cv2.imshow(const.PROJECT_NAME, frame)
            if self.process_key_event(cv2.waitKey(1)) == const.KEY_PROCESS_QUIT:
                break
            if cv2.getWindowProperty(const.PROJECT_NAME, cv2.WND_PROP_VISIBLE) < 1:
                break

        rval, frame = self.stream.read()
        frame = self.process_frame(frame, draw_interface=False)
        cv2.imwrite("mosaic_of_you.jpg", frame)


        for sec in range(const.END_SLEEP_SECS):
            text_width, text_height = cv2.getTextSize("Mosaic saved, exiting in {}...".format(const.END_SLEEP_SECS - sec), 
                                                      cv2.FONT_HERSHEY_SIMPLEX, 
                                                      3*const.TEXT_SCALE, 
                                                      2*const.TEXT_THICKNESS)[0]
            img = cv2.putText(np.copy(frame),
                             "Mosaic saved, exiting in {}...".format(const.END_SLEEP_SECS - sec), 
                             (const.LEFT_BORDER + int(const.IMAGE_WIDTH / 2 - text_width / 2) , const.TOP_BORDER + const.IMAGE_HEIGHT + 2*text_height),
                             cv2.FONT_HERSHEY_SIMPLEX,
                             3*const.TEXT_SCALE,
                             const.TEXT_COLOR,
                             2*const.TEXT_THICKNESS)
            cv2.imshow(const.PROJECT_NAME, img)
            cv2.waitKey(1)
            sleep(1)
                
        self.stream.release()
        cv2.destroyAllWindows()

    """
    Handles the user's key presses in order to simulate a text input field, as well as ESC as an exit command
    """
    def process_key_event(self, key):
        # Take least significant byte
        key = key & 0xFF
        if key == 255:
            return 0
        elif key == const.KEY_PROCESS_ESC:
            return -1
        elif key == const.KEY_PROCESS_CR or key == const.KEY_PROCESS_LF:
            self.submit_answer(self.user_text)
            self.user_text = ""
        elif key == const.KEY_PROCESS_BS:
            self.user_text = self.user_text[:-1]
        elif chr(key).isalnum():
            self.user_text += chr(key)
        elif chr(key) == ' ':
            self.user_text += ' '
        return 0

    """
    Processes a frame from the camera. Combines the sub images and tints them, resizes it, then adds the 
    borders and text
    """
    def process_frame(self, frame, draw_interface=True):
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
                        for list_h in tinged_imgs]), (const.IMAGE_WIDTH, const.IMAGE_HEIGHT))
                    
        img = cv2.copyMakeBorder(concatted_frame, 
                                             const.TOP_BORDER, 
                                             const.BOTTOM_BORDER, 
                                             const.LEFT_BORDER, 
                                             const.RIGHT_BORDER, 
                                             cv2.BORDER_CONSTANT)
        if draw_interface:
            img = self.draw_user_interface(img)

        return img

    """
    Draws the question and user's text input on the frame
    """
    def draw_user_interface(self, img):
        text_width, text_height = cv2.getTextSize(self.curr_question, cv2.FONT_HERSHEY_SIMPLEX, const.TEXT_SCALE, const.TEXT_THICKNESS)[0]
        img = cv2.putText(img,
                          self.curr_question, 
                          (const.LEFT_BORDER + int(const.IMAGE_WIDTH / 2 - text_width / 2) , const.TOP_BORDER + const.IMAGE_HEIGHT + 2*text_height),
                          cv2.FONT_HERSHEY_SIMPLEX,
                          const.TEXT_SCALE,
                          const.TEXT_COLOR,
                          const.TEXT_THICKNESS)

        img = cv2.rectangle(img,
                            const.TEXT_BOX_UL,
                            const.TEXT_BOX_LR,
                            const.TEXT_COLOR,
                            const.TEXT_BOX_THICKNESS)

        text_width, text_height = cv2.getTextSize(self.user_text, cv2.FONT_HERSHEY_PLAIN, const.TEXT_SCALE, const.TEXT_THICKNESS)[0]
        img = cv2.putText(img,
                          self.user_text,
                          (const.TEXT_BOX_UL[0] + const.USER_TEXT_XOFFSET, const.TEXT_BOX_LR[1] - const.USER_TEXT_YOFFSET),
                          cv2.FONT_HERSHEY_PLAIN,
                          const.USER_TEXT_SCALE,
                          const.TEXT_COLOR,
                          const.TEXT_THICKNESS)

        return img

    """
    Tinges an image the given rgb value
    """
    def tinge_img(self, img, rgb):
        # rgb must be a 3-tuple
        glass = np.full(img.shape, rgb, np.uint8)
        return cv2.addWeighted(img, const.IMG_TINGE_WEIGHTS[0], glass, const.IMG_TINGE_WEIGHTS[1], 0)


if __name__ == "__main__":
    Mosaic()