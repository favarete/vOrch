import cv2
from threading import Thread

class Webcam:
    def __init__(self, device):
        self.video_capture = cv2.VideoCapture(device)
        self.current_frame = self.video_capture.read()[1]
          
    def start(self):
        th = Thread(target=self._update_frame, args=())
        th.daemon = True
        th.start()
  
    def _update_frame(self):
        while(True):
            self.current_frame = self.video_capture.read()[1]
                  
    def get_current_frame(self):
        return self.current_frame

    def destroy(self):
    	self.video_capture.release()

    def get_resolution(self):
        return (self.video_capture.get(3), self.video_capture.get(4))

    def set_resolution(self, width, height):
        self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
