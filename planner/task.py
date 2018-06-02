from database import PATTERN, TASK

import cv2
from utils import *

DISTORTION = .4
SHAPE_RESIZE = 150.0

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

def process_frame(contours, img_rgb, img_gray, task_manager, robots_manager):

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

						robot_radius = get_robot_radius(ordered_points)
						frontX, frontY = get_pattern_front(i, ordered_points)
						cX, cY = get_central_points(c)
						Xc, Yc = get_extended_point(cX, cY, frontX, frontY, robot_radius)
						robots_manager[key]["node"][0] = [cX, cY]
						robots_manager[key]["node"][1] = [Xc, Yc]
						robots_manager[key]["indetified"] = True
						robots_manager[key]["radius"] = robot_radius
						cv2.drawContours(img_rgb, [approx], -1, DIMENSIONS_COLOR, LINE_THICKNESS)
						cv2.line(img_rgb, (cX, cY), (Xc, Yc), DIMENSIONS_COLOR, LINE_THICKNESS)
						cv2.circle(img_rgb, (cX, cY), DOT_SIZE, DIMENSIONS_COLOR, -1)
						cv2.circle(img_rgb, (cX, cY), robot_radius, DIMENSIONS_COLOR, LINE_THICKNESS)
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
	return img_rgb


def get_robot_radius(points):
	a = get_euclidean_distance(points[0][0], points[0][1], points[1][0], points[1][1])
	b = get_euclidean_distance(points[1][0], points[1][1], points[2][0], points[2][1])
	c = get_euclidean_distance(points[2][0], points[2][1], points[3][0], points[3][1])
	d = get_euclidean_distance(points[3][0], points[3][1], points[0][0], points[0][1])

	mean = np.divide(np.add(np.add(a,b), np.add(c,d)),4)
	radius = np.multiply(mean,1.5)

	return int(radius)