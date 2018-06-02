import kivy
kivy.require('1.10.0')

from kivy.lang import Builder
Builder.load_file('ui/layout.kv')

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.core.window import Window

import cv2
import numpy as np
from camera.webcam import Webcam
#from communication.network import Server
from threading import Thread
from database import SYSTEM_IDS
from utils import *
from planner.plan import make_plan
from planner.task import process_frame

'''
Kivy Configuration
'''
Window.size = (1245,640)
Window.left = 60
Window.top = 60

'''
OpenCV Configuration
'''
#Camera
_webcam = 1
_fps = 24
_resolution = (940, 780)
_calibrated_camera = True

number_of_robots = 1
CANNY_THRESHOLD = .7

# Find Robots
#server = Server()
#server.scan(number_of_robots)

# Initializations
robots_manager = { identification: {"node": np.empty((2, 2), dtype=int), 
									"radius": 0,
							 		"indetified": False,
							 		"running_plan": False } 
							 		for identification in SYSTEM_IDS[0] }

task_manager = {"solve_task": False,
				"busy": False,
				"task_ID": "",
				"solution_points":[],
				"solved_tasks": [],
				"busy_robots": 0  }


class CameraStream(Image):
		def __init__(self, fps=_fps, **kwargs):
			self.fps = fps
			super(CameraStream, self).__init__(**kwargs)

			self.webcam = Webcam(_webcam)
			self.webcam.start()
			self.webcam.set_resolution(_resolution[0], _resolution[1])

			Clock.schedule_interval(self.update, 1.0 / fps)

		def update(self, dt):
			img_rgb = self.webcam.get_current_frame()
			borders, n_img, img_gray = self.get_image_data(img_rgb)
			frame = process_frame(borders, n_img, img_gray, task_manager, robots_manager)

			texture = self.texture
			w, h = frame.shape[1], frame.shape[0]
			if not texture or texture.width != w or texture.height != h:
				self.texture = texture = Texture.create(size=(w, h))
				texture.flip_vertical()
			texture.blit_buffer(frame.tobytes(), colorfmt='bgr')
			self.canvas.ask_update()

		def get_image_data(self, img_rgb):
			img = img_rgb
			if _calibrated_camera:
				c_height,  c_width = img.shape[:2]
				c_newcameramtx, c_roi=cv2.getOptimalNewCameraMatrix(c_mtx,c_dist,(c_width,c_height),1,(c_width,c_height))
				# undistort
				c_dst = cv2.undistort(img, c_mtx, c_dist, None, c_newcameramtx)
				# crop the image
				c_x, c_y, c_width, c_height = c_roi
				c_dst = c_dst[c_y:c_y+c_height, c_x:c_x+c_width]
				raw_img = c_dst

			img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
			img_gray_blur = cv2.GaussianBlur(img_gray, (5, 5), 0)
			
			v = np.median(img_gray_blur)
			low = int(max(0, (1.0 - CANNY_THRESHOLD) * v))
			high = int(min(255, (1.0 + CANNY_THRESHOLD) * v))

			img_edges = cv2.Canny(img_gray_blur, low, high)

			kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
			img_edges_closed = cv2.morphologyEx(img_edges, cv2.MORPH_CLOSE, kernel)

			_, contours, _ = cv2.findContours(img_edges_closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

			return contours, img, img_gray

		def stop(self):
			self.webcam.destroy()

class View(GridLayout):
	pass

class visualOrchestrator(App):
	def build(self):
		self.view = View()
		self.camera_stream = self.view.ids.frame
		return self.view

	def on_stop(self):
		cv2.destroyAllWindows()
		self.camera_stream.stop()
		pass

if __name__ == "__main__":
	# Calibration 
	if _calibrated_camera:
		from pathlib import Path
		calibration_data = Path.cwd() / "camera" / "calibration_data" / "pattern" / "chessboard" / "calibration_ouput.npz"
		npzfile = np.load(calibration_data)
		c_ret = npzfile["ret"] 
		c_mtx = npzfile["mtx"]
		c_dist = npzfile["dist"]
		c_rvecs = npzfile["rvecs"]
		c_tvecs = npzfile["tvecs"]

	visualOrchestrator().run()