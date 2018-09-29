from database import PATTERN, TASK

import cv2
import _global_
from utils import *

SHAPE_RESIZE = 150.0

# VISUAL CONFIGURATION
FONT_BIG = cv2.FONT_HERSHEY_SIMPLEX	
TEXT_SIZE_BIG = 0.6
TEXT_SIZE_MEDIUM = 0.4
DIMENSIONS_COLOR = (70, 255, 110)
FONT_COLOR = (255, 55, 0)
FONT_COLOR_TASK = (70, 90, 255)
BOLD = 2
THIN = 1
DOT_SIZE = 7
TASK_COLOR = (70, 80, 255)
SOLUTION_COLOR = (255, 255, 0)
LINE_THICKNESS = 4 

BAD_STATUS_COLOR = (10, 10, 255)
GOOD_STATUS_COLOR = (10, 255, 10)

def process_frame(contours, img_gray, visible_img):

	for c in contours:
		# Approximate the contour
		peri = cv2.arcLength(c, True)
		approx = cv2.approxPolyDP(c, 0.04 * peri, True)

		if is_valid_square(approx, _global_.gui_properties["section_2"]["variable_sqrdst"]):
			robot_found = False
			task_found = False
					
			#reposition of glyph
			ordered_points, topdown_quad = get_topdown_quad(img_gray, approx.reshape(4, 2))
			resized_shape = resize_image(topdown_quad, SHAPE_RESIZE)

			if resized_shape[5, 5] > 170: 
				continue
	 				
	 		glyph_pattern = get_glyph_pattern(resized_shape)

	 		if _global_.gui_properties["section_1b"]["all_squares_view"]:
				cv2.drawContours(visible_img, [approx], -1, DIMENSIONS_COLOR, LINE_THICKNESS/2)

			for key, value in PATTERN.iteritems():
				for i in range(4):
					if glyph_pattern == value[i]: 
						robot_found = True

						robot_radius = get_robot_radius(ordered_points)
						frontX, frontY = get_pattern_front(i, ordered_points)
						cX, cY = get_central_points(c)
						Xc, Yc = get_extended_point(cX, cY, frontX, frontY, robot_radius)
						_global_.robots_manager[key]["node"][0] = [cX, cY]
						_global_.robots_manager[key]["node"][1] = [Xc, Yc]
						_global_.robots_manager[key]["indetified"] = True
						_global_.robots_manager[key]["radius"] = robot_radius
						if _global_.gui_properties["section_1b"]["detection_view"]:
							cv2.drawContours(visible_img, [approx], -1, DIMENSIONS_COLOR, LINE_THICKNESS)
							cv2.line(visible_img, (cX, cY), (Xc, Yc), DIMENSIONS_COLOR, LINE_THICKNESS)
							cv2.circle(visible_img, (cX, cY), DOT_SIZE, DIMENSIONS_COLOR, -1)
							cv2.circle(visible_img, (cX, cY), robot_radius, DIMENSIONS_COLOR, LINE_THICKNESS)
							cv2.putText(visible_img, key, 
										(cX - 5, cY - 15), 
										FONT_BIG, 
										TEXT_SIZE_BIG, 
										FONT_COLOR, 
										BOLD, 
										cv2.LINE_AA)
							battery_feedback = _global_.robots_manager[key]["battery"].splitlines()

							if len(battery_feedback) > 0:
								color = None
								if battery_feedback[0] == "Good":
									color = GOOD_STATUS_COLOR
								else:
									color = BAD_STATUS_COLOR
								cv2.putText(visible_img,
										battery_feedback[0],
										(cX - 5, cY), 
										FONT_BIG, 
										TEXT_SIZE_MEDIUM, 
										color, 
										THIN, 
										cv2.LINE_AA)

								if battery_feedback[1] == "Good":
									color = GOOD_STATUS_COLOR
								else:
									color = BAD_STATUS_COLOR
								cv2.putText(visible_img,
										battery_feedback[1],
										(cX - 5, cY + 15), 
										FONT_BIG, 
										TEXT_SIZE_MEDIUM, 
										color, 
										THIN, 
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
							_global_.task_manager["solve_task"] = True
							frontX, frontY = get_pattern_front(i, ordered_points)
							centerX, centerY = get_central_points(c)
							# List of solutions for the known tasks
							if key == "ID::A":
								topX, topY = get_extended_point(centerX, centerY, frontX, frontY, value["dimension"])
								solution_points = get_polyline_list([topX, topY])
								_global_.task_manager["solution_points"] = solution_points
								_global_.task_manager["busy_robots"] += value["difficult"]
								#TODO: Use this if it's busy on some task
								_global_.task_manager["task_ID"] = key

								if _global_.gui_properties["section_1b"]["detection_view"]:
									cv2.circle(visible_img, (topX, topY), DOT_SIZE, SOLUTION_COLOR, -1)
									cv2.polylines(visible_img, [solution_points], True, SOLUTION_COLOR, 1)
									cv2.putText(visible_img, "Solution", 
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
								_global_.task_manager["solution_points"] = solution_points
								_global_.task_manager["busy_robots"] += value["difficult"]
								#TODO: Use this if it's busy on some task
								_global_.task_manager["task_ID"] = key

								if _global_.gui_properties["section_1b"]["detection_view"]:
									cv2.circle(visible_img, (topX, topY), DOT_SIZE, SOLUTION_COLOR, -1)
									cv2.circle(visible_img, (baseLeftX, baseLeftY), DOT_SIZE, SOLUTION_COLOR, -1)
									cv2.circle(visible_img, (baseRightX, baseRightY), DOT_SIZE, SOLUTION_COLOR, -1)										
									cv2.polylines(visible_img, [solution_points], True, SOLUTION_COLOR, 1)
									cv2.putText(visible_img, "Solution", 
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
								_global_.task_manager["solution_points"] = solution_points
								_global_.task_manager["busy_robots"] += value["difficult"]
								#TODO: Use this if it's busy on some task
								_global_.task_manager["task_ID"] = key

								if _global_.gui_properties["section_1b"]["detection_view"]:
									cv2.circle(visible_img, (topX, topY), DOT_SIZE, SOLUTION_COLOR, -1)
									cv2.circle(visible_img, (baseX, baseY), DOT_SIZE, SOLUTION_COLOR, -1)
									cv2.polylines(visible_img, [solution_points], True, SOLUTION_COLOR, 1)
									cv2.putText(visible_img, "Solution", 
												(topX - 5, topY - 15), 
												FONT_BIG, 
												TEXT_SIZE_BIG, 
												SOLUTION_COLOR, 
												BOLD, 
												cv2.LINE_AA)

							if _global_.gui_properties["section_1b"]["detection_view"]:
								cv2.drawContours(visible_img, [approx], -1, TASK_COLOR, LINE_THICKNESS)
								cv2.circle(visible_img, (centerX, centerY), DOT_SIZE, TASK_COLOR, -1)
										
								cv2.putText(visible_img, key, 
											(centerX - 5, centerY - 15), 
											FONT_BIG, 
											TEXT_SIZE_BIG, 
											FONT_COLOR_TASK, 
											BOLD, 
											cv2.LINE_AA)
							break
					if task_found:
						break
	return visible_img


def get_robot_radius(points):
	a = get_euclidean_distance(points[0][0], points[0][1], points[1][0], points[1][1])
	b = get_euclidean_distance(points[1][0], points[1][1], points[2][0], points[2][1])
	c = get_euclidean_distance(points[2][0], points[2][1], points[3][0], points[3][1])
	d = get_euclidean_distance(points[3][0], points[3][1], points[0][0], points[0][1])

	mean = np.divide(np.add(np.add(a,b), np.add(c,d)),4)
	radius = np.multiply(mean,1.5)

	return int(radius)