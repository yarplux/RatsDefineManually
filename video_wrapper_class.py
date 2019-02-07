import cv2
import numpy as np

import config as cfg

class MyVideo:
    vid = cv2.VideoCapture()
    counter = 0
    frame = np.zeros((0, 0, 3), np.uint8)

    def __init__(self, video_source=''):
        self.vid = cv2.VideoCapture(video_source)
        self.length = self.vid.get(cv2.CAP_PROP_FRAME_COUNT)

        self.current_width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.current_height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

        self.width = int(self.current_width*cfg.opt_process['k'])
        self.height = int(self.current_height*cfg.opt_process['k'])

        if self.vid.isOpened():
            ret, frame = self.vid.read()
            MyVideo.frame = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), (self.width, self.height))

        else:
            raise ValueError("Unable to open video source", video_source)

    def get_frame(self):
        if self.vid.isOpened():
            MyVideo.counter += cfg.opt_process['FrameDelta']
            if MyVideo.counter >= self.length:
                MyVideo.counter = 0

            self.vid.set(cv2.CAP_PROP_POS_FRAMES, MyVideo.counter)
            ret, frame = self.vid.read()
            if ret:
                MyVideo.frame = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), (int(self.width), int(self.height)))

            return ret, MyVideo.frame
        else:
            return False, None

    def set_frame(self, x):
        self.vid.set(cv2.CAP_PROP_POS_FRAMES, x)
        ret, frame = self.vid.read()
        if ret:
            MyVideo.frame = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), (int(self.width), int(self.height)))

        MyVideo.counter = x

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()