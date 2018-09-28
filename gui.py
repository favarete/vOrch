import kivy
kivy.require('1.10.0')

from kivy.lang import Builder
Builder.load_file('ui/layout.kv')

import _global_

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics.vertex_instructions import (Ellipse, Line, Rectangle)
from kivy.graphics.context_instructions import Color
from kivy.graphics.scissor_instructions import (ScissorPush, ScissorPop)

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
		new_string = ''
		if data == None:
			new_string = "No Plans to Execute"
			_global_.gui_properties['section_4']['points'] = []
		else:
			for key, value in data.iteritems():
				temp_string1 = "\nRobot ID " + key[4:] + "\n"
				temp_string2 = "Plan: Sequence>>"

				temp_string3 = ''.join([ str(txt) +'\n' if i % 2 == 0
						 	   else str(txt) + '>' for i, txt in enumerate(value, 1)])

				new_string += temp_string1 + temp_string2 + temp_string3 + "\n"

		self.ids.planner_feedback.text = new_string

	def set_variables(self, instance):
		filters = _global_.gui_properties["section_2"]
		filters[instance.name] = type(filters[instance.name])(instance.value)

		if instance.name == "variable_fps":
			self.ids.frame.reschedule_clock()
	
	def toggle_server(self, instance):
		if instance.state == "down":
			instance.text = "Connected"
			thread1 = serverThread(2)
			thread1.start()
		else:
			instance.text = "Connect"
			_global_.server = None
			_global_.task_manager["available_robot"] = False
			for robot in _global_.robots_manager:
				_global_.robots_manager[robot]["hardware"] = None

class serverThread(Thread):
	def __init__(self, number_of_robots):
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

class PlanView(AnchorLayout):
	def __init__(self, **kwargs):
		super(PlanView, self).__init__(**kwargs)
		self.timer = Clock.schedule_interval(self.update, 1.0 /24)

		self.windowX = Window.size[0]
		self.windowY = Window.size[1]
		self.x0 = 840
		self.y0 = 210
		self.x1 = 1225
		self.y1 = 25
		self.refx0 = 10
		self.refx1 = 810
		self.refy0 = 618
		self.refy1 = 20

	def update(self, *args):
		data = self.extract_points(_global_.gui_properties['section_4']['points'])
		self.draw_lines(data)

	def extract_points(self, dict_data):
		data = []
		for each in dict_data:
			aux1 = dict_data[each]['points']
			aux2 = []
			for i in _global_.robots_manager[each]["node"][0]:
				aux2.append(i)
			for i in aux1:
				for j in i:
					aux2.append(j)
			data.append(aux2)
		for i in data:
			for j in range(len(i)):
				if j % 2 != 0:
					value = 720 - i[j]
					i[j] = self.change_size(value, 'y')
				else:
					i[j] = self.change_size(i[j], 'x')
		return data

	def change_size(self, value, axis):
		old_rangeX = self.refx1 - self.refx0
		old_rangeY = self.refy1 - self.refy0
		
		new_value = 0
		if (axis == 'x'):
			if (old_rangeX == 0):
				new_value = self.x0
			else:
				new_range = self.x1 - self.x0
				new_value = (((value - self.refx0) * new_range) / old_rangeX) + self.x0
		elif (axis == 'y'):
			if (old_rangeX == 0):
				new_value = self.y0
			else:
				new_range = self.y1 - self.y0
				new_value = (((value - self.refy0) * new_range) / old_rangeY) + self.y0
		return new_value

	def draw_lines(self, data):
		self.canvas.after.clear()
		self.canvas.clear()

		self.inner_radius = 30
		self.outer_radius = 33

		with self.canvas:
			self.rect1 = Rectangle(pos=[self.x, self.y - 8], 
								   size=[self.width, self.height - 2],
								   color=Color(.1, .1, .1))
			self.rect2 = Rectangle(pos=[self.x + 15, self.y + 5], 
								   size=[self.width - 30, self.height - 30],
								   color=Color(0, 0, 0))
		for i in range(len(data)):
			with self.canvas.after:
				ScissorPush(x=int(self.x + 15), y=int(self.y + 5),
							width=int(self.width - 30), height=int(self.height - 30))

				self.color = Color(.22, .71 * i, .91)
				self.line = Line(points=data[i],
								 close=False,
								 width = 2)
				for j,k in zip(data[i][0::2], data[i][1::2]):
					self.color = Color(.22, .71 * i, .91)
					self.el0 = Ellipse(pos=(j - self.inner_radius/2, 
											k - self.inner_radius/2), 
											size=(self.inner_radius,
											self.inner_radius))
					self.color = Color(.1, .1, .1)
					self.el1 = Ellipse(pos=(j - self.inner_radius * .45, 
											k - self.inner_radius * .45), 
											size=(self.inner_radius *.9, 
											self.inner_radius * .9))
					self.color = Color(.22, .71 * i, .91)
					self.el = Ellipse(pos=(j - self.inner_radius*.25, 
										   k - self.inner_radius*.25), 
										   size=(self.inner_radius *.5,
										   self.inner_radius*.5))
					self.el0 = Line(circle=(j, k, self.outer_radius))
				ScissorPop()

		self.x0 = self.rect2.pos[0]
		self.y0 = self.rect2.size[1]
		self.x1 = self.x0 + self.rect2.size[0] - 80
		self.y1 = self.rect2.pos[1] + 20



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