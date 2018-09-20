import kivy
kivy.require('1.10.0')

from kivy.lang import Builder
Builder.load_file('ui/layout.kv')

import _global_

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.core.window import Window

import cv2
import numpy as np

from threading import Thread

from camera.webcam import Webcam
from utils import *
from communication.network import Server
from planner.plan import run_planner
from planner.task import process_frame

Window.size = (1245,640)
Window.left = 60
Window.top = 60

'''
OpenCV Configuration
'''

#Camera
_webcam = 1
_resolution = (940, 780)

class CameraStream(Image):
		def __init__(self, **kwargs):
			super(CameraStream, self).__init__(**kwargs)

			self.webcam = Webcam(_webcam)
			self.webcam.start()
			self.webcam.set_resolution(_resolution[0], _resolution[1])
			self.timer = Clock.schedule_interval(self.update, 
				1.0 / _global_.gui_properties["section_2"]["variable_fps"])

		def reschedule_clock(self):
			self.timer.cancel()
			self.timer = Clock.schedule_interval(self.update, 
				1.0 / _global_.gui_properties["section_2"]["variable_fps"])

		def update(self, dt):
			img_rgb = self.webcam.get_current_frame()
			contours, visible_img, img_gray= self.get_image_data(img_rgb)
			frame = process_frame(contours,
								  img_gray,
								  visible_img)
			run_planner()
			self.parent.parent.show_plan()

			texture = self.texture
			w, h = frame.shape[1], frame.shape[0]
			if not texture or texture.width != w or texture.height != h:
				self.texture = texture = Texture.create(size=(w, h))
				texture.flip_vertical()
			texture.blit_buffer(frame.tobytes(), colorfmt='bgr')
			self.canvas.ask_update()

		def get_image_data(self, img):
			img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
			img_gray_blur = cv2.GaussianBlur(img_gray, 
				(_global_.gui_properties["section_2"]["variable_blur"], 
				 _global_.gui_properties["section_2"]["variable_blur"]), 0)
			
			v = np.median(img_gray_blur)
			low = int(max(0, (1.0 - _global_.gui_properties["section_2"]["variable_cannyt"]) * v))
			high = int(min(255, (1.0 + _global_.gui_properties["section_2"]["variable_cannyt"]) * v))

			img_edges = cv2.Canny(img_gray_blur, low, high)

			kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
			img_edges_closed = cv2.morphologyEx(img_edges, cv2.MORPH_CLOSE, kernel)

			_, contours, _ = cv2.findContours(img_edges_closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

			if _global_.gui_properties["section_1a"]["filter_borders"]:
				img = cv2.cvtColor(img_edges_closed, cv2.COLOR_GRAY2BGR)
			elif _global_.gui_properties["section_1a"]["filter_gray"]:
				img = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2BGR) 
			elif _global_.gui_properties["section_1a"]["filter_blur"]:
				img = cv2.cvtColor(img_gray_blur, cv2.COLOR_GRAY2BGR) 

			return contours, img, img_gray

		def stop(self):
			self.webcam.destroy()

class View(GridLayout):
	def set_view(self, instance):
		filters = _global_.gui_properties["section_1a"]
		for btn in filters:
			if instance.name == btn and instance.state == "down":
				filters[btn] = True
			else:
				self.ids[btn].state = "normal"
				filters[btn] = False

	def set_feeback(self, instance):
		filters = _global_.gui_properties["section_1b"]
		filters[instance.name] = instance.active

	def show_plan(self):
		data = _global_.gui_properties["section_4"]["plan"]
		if data == None:
			new_string = "No Plans to Execute"
		else:
			for key, value in data.iteritems():
				temp_string1 = "Robot ID " + key[4:] + "\n"
				temp_string2 = "Plan: Sequence>"
				temp_string3 = '>'.join(map(str, value))

			new_string = temp_string1 + temp_string2 + temp_string3 + "\n\n"

		self.ids.planner_feedback.text = new_string

	def set_variables(self, instance):
		filters = _global_.gui_properties["section_2"]
		filters[instance.name] = type(filters[instance.name])(instance.value)

		if instance.name == "variable_fps":
			self.ids.frame.reschedule_clock()
	
	def toggle_server(self, instance):
		if instance.state == "down":
			instance.text = "Connected"
			thread1 = serverThread(1)
			thread1.start()
		else:
			instance.text = "Connect"
			_global_.server = None
			_global_.task_manager["available_robot"] = False
			for robot in _global_.robots_manager:
				_global_.robots_manager[robot]["hardware"] = None

class serverThread(Thread):
	def __init__(self, server, number_of_robots=1):
		super(serverThread, self).__init__()
		self.daemon = True
		self.number_of_robots = number_of_robots

	def run(self):
		_global_.server = Server()
		_global_.server.scan(self.number_of_robots)
		self.associate_robots()

	def associate_robots(self):
		for robot in _global_.robots_manager:
			_global_.robots_manager[robot]["hardware"] = _global_.server.getRobot(robot[-2:])
		if _global_.server.robotsOnline > 0:
			_global_.task_manager["available_robot"] = True

class visualOrchestrator(App):
	def build(self):
		self.view = View()
		self.camera_stream = self.view.ids.frame
		return self.view

	def on_stop(self):
		cv2.destroyAllWindows()
		self.camera_stream.stop()

if __name__ == "__main__":
	visualOrchestrator().run()