from camera.webcam import Webcam
#from communication.network import Server
from threading import Thread
from database import PATTERN, TASK
from utils import *
from planner.plan import make_plan

import numpy as np
import cv2

# CONFIGURATION
camera = 1
number_of_robots = 1
calibrated_camera = True

ROBOT_RADIUS = 100
DISTORTION = .4
SHAPE_RESIZE = 150.0
CANNY_THRESHOLD = .7

# VISUAL CONFIGURATION
FONT_BIG = cv2.FONT_HERSHEY_SIMPLEX	
TEXT_SIZE_BIG = 0.6
DIMENSIONS_COLOR = (70, 255, 110)
FONT_COLOR = (255, 55, 0)
FONT_COLOR_TASK = (70, 90, 255)
BOLD = 2
DOT_SIZE = 7
TASK_COLOR = (70, 80, 255)
SOLUTION_COLOR = (255, 255, 0)
LINE_THICKNESS = 4 

# auxiliar constants
INTERSECTION_THRESHOLD = 2 * ROBOT_RADIUS

# Find Robots
#server = Server()
#server.scan(number_of_robots)

# Initializations
robot_ids = PATTERN.keys()
robots_pos = { identification: {"node": np.empty((2, 2), dtype=int), 
								"diameter": 2 * ROBOT_RADIUS,
#								"hardware": server.getRobot(identification[-2:]), 
							 	"indetified": False,
							 	"running_plan": False } 
							 	for identification in robot_ids }

task_ids = TASK.keys()

task_manager = {"solve_task": False,
				"busy": False,
				"task_ID": "",
				"solution_points":[],
				"solved_tasks": [],
				"busy_robots": 0  }

# Initialize Webcam thread
webcam = Webcam(camera)
webcam.start()

# Calibration 
if calibrated_camera:
	from pathlib import Path
	calibration_data = Path.cwd() / "camera" / "calibration_data" / "pattern" / "chessboard" / "calibration_ouput.npz"
	npzfile = np.load(calibration_data)
	c_ret = npzfile["ret"] 
	c_mtx = npzfile["mtx"]
	c_dist = npzfile["dist"]
	c_rvecs = npzfile["rvecs"]
	c_tvecs = npzfile["tvecs"]

try:
	while True:
		img_rgb = webcam.get_current_frame()

		if calibrated_camera:
			c_height,  c_width = img_rgb.shape[:2]
			c_newcameramtx, c_roi=cv2.getOptimalNewCameraMatrix(c_mtx,c_dist,(c_width,c_height),1,(c_width,c_height))
			# undistort
			c_dst = cv2.undistort(img_rgb, c_mtx, c_dist, None, c_newcameramtx)

			# crop the image
			c_x, c_y, c_width, c_height = c_roi
			c_dst = c_dst[c_y:c_y+c_height, c_x:c_x+c_width]
			img_rgb = c_dst

		img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY) 
		img_gray_blur = cv2.GaussianBlur(img_gray, (5, 5), 0)
		
		v = np.median(img_gray_blur)
		low = int(max(0, (1.0 - CANNY_THRESHOLD) * v))
		high = int(min(255, (1.0 + CANNY_THRESHOLD) * v))

		img_edges = cv2.Canny(img_gray_blur, low, high)

		kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
		img_edges_closed = cv2.morphologyEx(img_edges, cv2.MORPH_CLOSE, kernel)

		#cv2.imshow('debug',img_edges_closed)

		_, contours, _ = cv2.findContours(img_edges_closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		
		for c in contours:
			# Approximate the contour
			peri = cv2.arcLength(c, True)
			approx = cv2.approxPolyDP(c, 0.04 * peri, True)

			if is_valid_square(approx, DISTORTION):
				robot_found = False
				task_found = False
				
				#reposition of glyph
				ordered_points, topdown_quad = get_topdown_quad(img_gray, approx.reshape(4, 2))
				resized_shape = resize_image(topdown_quad, SHAPE_RESIZE)

				if resized_shape[5, 5] > 170: 
					continue
 				
 				glyph_pattern = get_glyph_pattern(resized_shape)

 				#Draw all squares found
				#cv2.drawContours(img_rgb, [approx], -1, DIMENSIONS_COLOR, LINE_THICKNESS/2)

				for key, value in PATTERN.iteritems():
					for i in range(4):

						if glyph_pattern == value[i]: 
							robot_found = True

							frontX, frontY = get_pattern_front(i, ordered_points)
							cX, cY = get_central_points(c)
							Xc, Yc = get_extended_point(cX, cY, frontX, frontY, ROBOT_RADIUS)

							robots_pos[key]["node"][0] = [cX, cY]
							robots_pos[key]["node"][1] = [Xc, Yc]
							robots_pos[key]["indetified"] = True

							cv2.drawContours(img_rgb, [approx], -1, DIMENSIONS_COLOR, LINE_THICKNESS)
							cv2.line(img_rgb, (cX, cY), (Xc, Yc), DIMENSIONS_COLOR, LINE_THICKNESS)
							cv2.circle(img_rgb, (cX, cY), DOT_SIZE, DIMENSIONS_COLOR, -1)
							cv2.circle(img_rgb, (cX, cY), ROBOT_RADIUS, DIMENSIONS_COLOR, LINE_THICKNESS)
							cv2.putText(img_rgb, key, 
									   (cX - 5, cY - 15), 
									   FONT_BIG, 
									   TEXT_SIZE_BIG, 
									   FONT_COLOR, 
									   BOLD, 
									   cv2.LINE_AA)
							break
					if robot_found:
						break

				if not robot_found:
					for key, value in TASK.iteritems():
						for i in range(4):
							if glyph_pattern == value["matrix"][i]: 
								task_found = True

								#TODO: Use this if it's busy on some task
								task_manager["solve_task"] = True

								frontX, frontY = get_pattern_front(i, ordered_points)
								centerX, centerY = get_central_points(c)

								# List of solutions for the known tasks
								if key == "ID::A":
									topX, topY = get_extended_point(centerX, centerY, frontX, frontY, value["dimension"])

									solution_points = get_polyline_list([topX, topY])

									task_manager["solution_points"] = solution_points
									task_manager["busy_robots"] += value["difficult"]

									#TODO: Use this if it's busy on some task
									task_manager["task_ID"] = key

									cv2.circle(img_rgb, (topX, topY), DOT_SIZE, SOLUTION_COLOR, -1)
									
									cv2.polylines(img_rgb, [solution_points], True, SOLUTION_COLOR, 1)
									cv2.putText(img_rgb, "Solution", 
										   (topX - 5, topY - 15), 
										   FONT_BIG, 
										   TEXT_SIZE_BIG, 
										   SOLUTION_COLOR, 
										   BOLD, 
										   cv2.LINE_AA)
								
								elif key == "ID::B":
									topX, topY = get_extended_point(centerX, centerY, frontX, frontY, value["dimension"][0])
									baseX, baseY = get_extended_point(centerX, centerY, frontX, frontY, -value["dimension"][1])
									auxX, auxY = get_extended_point(baseX, baseY, centerX, centerY, -value["dimension"][2])
									baseLeftX, baseLeftY, baseRightX, baseRightY = get_perpendicular_points(baseX, baseY, auxX, auxY)

									solution_points = get_polyline_list([topX, topY, baseLeftX, baseLeftY, baseRightX, baseRightY])

									task_manager["solution_points"] = solution_points
									task_manager["busy_robots"] += value["difficult"]

									#TODO: Use this if it's busy on some task
									task_manager["task_ID"] = key

									cv2.circle(img_rgb, (topX, topY), DOT_SIZE, SOLUTION_COLOR, -1)
									cv2.circle(img_rgb, (baseLeftX, baseLeftY), DOT_SIZE, SOLUTION_COLOR, -1)
									cv2.circle(img_rgb, (baseRightX, baseRightY), DOT_SIZE, SOLUTION_COLOR, -1)

									
									cv2.polylines(img_rgb, [solution_points], True, SOLUTION_COLOR, 1)
									cv2.putText(img_rgb, "Solution", 
										   (topX - 5, topY - 15), 
										   FONT_BIG, 
										   TEXT_SIZE_BIG, 
										   SOLUTION_COLOR, 
										   BOLD, 
										   cv2.LINE_AA)

								elif key == "ID::C":
									topX, topY = get_extended_point(centerX, centerY, frontX, frontY, value["dimension"])
									baseX, baseY = get_extended_point(centerX, centerY, frontX, frontY, -value["dimension"])

									solution_points = get_polyline_list([topX, topY, baseX, baseY])

									task_manager["solution_points"] = solution_points
									task_manager["busy_robots"] += value["difficult"]

									#TODO: Use this if it's busy on some task
									task_manager["task_ID"] = key

									cv2.circle(img_rgb, (topX, topY), DOT_SIZE, SOLUTION_COLOR, -1)
									cv2.circle(img_rgb, (baseX, baseY), DOT_SIZE, SOLUTION_COLOR, -1)

									cv2.polylines(img_rgb, [solution_points], True, SOLUTION_COLOR, 1)
									cv2.putText(img_rgb, "Solution", 
										   (topX - 5, topY - 15), 
										   FONT_BIG, 
										   TEXT_SIZE_BIG, 
										   SOLUTION_COLOR, 
										   BOLD, 
										   cv2.LINE_AA)

								
								cv2.drawContours(img_rgb, [approx], -1, TASK_COLOR, LINE_THICKNESS)
								cv2.circle(img_rgb, (centerX, centerY), DOT_SIZE, TASK_COLOR, -1)
								
								cv2.putText(img_rgb, key, 
									   (centerX - 5, centerY - 15), 
									   FONT_BIG, 
									   TEXT_SIZE_BIG, 
									   FONT_COLOR_TASK, 
									   BOLD, 
									   cv2.LINE_AA)
								break
						if task_found:
							break
		#Start making plan
		'''
		if task_manager["solve_task"] and robot_found:
			if not task_manager["busy"]:
				task_manager["busy"] = True
				plan = make_plan(robots_pos, task_manager)
				for r in plan:
					if len(plan[r]) > 0:
						Thread(target=robots_pos[r]["hardware"].run_plan, args=(plan[r], robots_pos)).start()
			else:
				check = all(value["running_plan"] == False for key, value in robots_pos.iteritems())
				if check:
					task_manager["busy"] = False
					task_manager["solve_task"] = False
					print "All plans executed!"
				pass
		'''
		
		cv2.imshow('feedback',img_rgb)
		cv2.waitKey(10)

except KeyboardInterrupt:
	webcam.destroy()
	cv2.destroyAllWindows()
