from webcam import Webcam
from database import PATTERN, TASK
from utils import *
import cv2

# CONFIGURATION
camera = 1

ROBOT_RADIUS = 100
DISTORTION = .3
MIN_SQUARE_AREA = 5000
MAX_SQUARE_AREA = 15000
SHAPE_RESIZE = 150.0
BLACK_THRESHOLD = 100
WHITE_THRESHOLD = 150

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

# Initializations
robot_ids = PATTERN.keys()
robots_pos = { identification: {"posCenterX":0, 
							 	"posCenterY":0, 
							 	"posFrontX":0, 
							 	"posFrontY":0,
							 	"indetified": False } 
							 	for identification in robot_ids }

task_ids = TASK.keys()

task_manager = {"solving_task": False,
				"task_ID": "",
				"solution_points":[],
				"busy_robots": 0  }

# Initialize Webcam thread
webcam = Webcam(camera)
webcam.start()

try:
	while True:
		img_rgb = webcam.get_current_frame()

		img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
		img_gray_blur = cv2.GaussianBlur(img_gray, (3, 3), 0)
		img_edges = cv2.Canny(img_gray_blur, 45, 60)

		kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
		img_edges_closed = cv2.morphologyEx(img_edges, cv2.MORPH_CLOSE, kernel)

		_, contours, _ = cv2.findContours(img_edges_closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

		for c in contours:
			# Approximate the contour
			peri = cv2.arcLength(c, True)
			approx = cv2.approxPolyDP(c, 0.01 * peri, True)

			if is_valid_square(approx, DISTORTION, MIN_SQUARE_AREA, MAX_SQUARE_AREA):
				robot_found = False
				task_found = False
				
				#reposition of glyph
				ordered_points, topdown_quad = get_topdown_quad(img_gray, approx.reshape(4, 2))
				resized_shape = resize_image(topdown_quad, SHAPE_RESIZE)

				if resized_shape[5, 5] > BLACK_THRESHOLD: 
					continue
 				
 				glyph_pattern = get_glyph_pattern(resized_shape, BLACK_THRESHOLD, WHITE_THRESHOLD)

 				#Draw all squares found
				#cv2.drawContours(img_rgb, [approx], -1, DIMENSIONS_COLOR, LINE_THICKNESS/2)

				for key, value in PATTERN.iteritems():
					for i in range(4):

						if glyph_pattern == value[i]: 
							robot_found = True

							frontX, frontY = get_pattern_front(i, ordered_points)
							cX, cY = get_central_points(c)
							Xc, Yc = get_extended_point(cX, cY, frontX, frontY, ROBOT_RADIUS)

							robots_pos[key]["posCenterX"] = cX
							robots_pos[key]["posCenterY"] = cY
							robots_pos[key]["posFrontX"] = Xc
							robots_pos[key]["posFrontY"] = Yc
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
								task_manager["solving_task"] = True

								frontX, frontY = get_pattern_front(i, ordered_points)
								centerX, centerY = get_central_points(c)


								# List of solutions for the known tasks
								if key == "ID::A":
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

		cv2.imshow('feedback',img_rgb)
		cv2.waitKey(10)

except KeyboardInterrupt:
	webcam.destroy()
	cv2.destroyAllWindows()