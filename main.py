from webcam import Webcam
from database import PATTERN
from utils import *
import cv2

# CONFIGURATION
camera = 1

ROBOT_RADIUS = 100
DISTORTION = .3
MIN_SQUARE_AREA = 5000
MAX_SQUARE_AREA = 15000
SHAPE_RESIZE = 100.0
BLACK_THRESHOLD = 50
WHITE_THRESHOLD = 100

# VISUAL CONFIGURATION
FONT_BIG = cv2.FONT_HERSHEY_SIMPLEX	
TEXT_SIZE_BIG = 0.6
DIMENSIONS_COLOR = (0, 255, 0)
FONT_COLOR = (255, 55, 0)
BOLD = 2
DOT_SIZE = 7

# auxiliar constants
INTERSECTION_THRESHOLD = 2 * ROBOT_RADIUS

# Initializations
robot_ids = PATTERN.keys()
robots = { identification: { "centerX":0, 
							 "centerY":0, 
							 "frontX":0, 
							 "frontY":0 } 
							 for identification in robot_ids }

# Initialize Webcam thread
webcam = Webcam(camera)
webcam.start()

try:
	while True:
		img_rgb = webcam.get_current_frame()

		img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
		img_gray_blur = cv2.GaussianBlur(img_gray, (3, 3), 0)
		img_edges = cv2.Canny(img_gray_blur, 45, 60)

		kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 10))
		img_edges_closed = cv2.morphologyEx(img_edges, cv2.MORPH_CLOSE, kernel)

		_, contours, _ = cv2.findContours(img_edges_closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

		glyph_found = False
		for c in contours:
			# Approximate the contour
			peri = cv2.arcLength(c, True)
			approx = cv2.approxPolyDP(c, 0.01 * peri, True)

			if is_valid_square(approx, DISTORTION, MIN_SQUARE_AREA, MAX_SQUARE_AREA):
				
				#reposition of glyph
				ordered_points, topdown_quad = get_topdown_quad(img_gray, approx.reshape(4, 2))
				resized_shape = resize_image(topdown_quad, SHAPE_RESIZE)

				if resized_shape[5, 5] > BLACK_THRESHOLD: 
					continue
 				
 				glyph_pattern = get_glyph_pattern(resized_shape, BLACK_THRESHOLD, WHITE_THRESHOLD)

				cv2.drawContours(img_rgb, [approx], -1, DIMENSIONS_COLOR, 4)

				for key, value in PATTERN.iteritems():
					for i in range(4):

						if glyph_pattern == value[i]: 
							glyph_found = True

							frontX, frontY = get_pattern_front(i, ordered_points)

							cX, cY = get_central_points(c)
							Xc, Yc = get_collision_point(cX, cY, frontX, frontY, ROBOT_RADIUS)

							robots[key]["centerX"] = cX
							robots[key]["centerY"] = cY
							robots[key]["frontX"] = Xc
							robots[key]["frontY"] = Yc

							cv2.line(img_rgb, (cX, cY), (Xc, Yc), DIMENSIONS_COLOR, 4)
							cv2.circle(img_rgb, (cX, cY), DOT_SIZE, DIMENSIONS_COLOR, -1)
							cv2.circle(img_rgb, (cX, cY), ROBOT_RADIUS, DIMENSIONS_COLOR, 4)
							cv2.putText(img_rgb, key, 
									   (cX - 5, cY - 15), 
									   FONT_BIG, 
									   TEXT_SIZE_BIG, 
									   FONT_COLOR, 
									   BOLD, 
									   cv2.LINE_AA)
							break

		cv2.imshow('feedback',img_rgb)
		cv2.waitKey(10)

except KeyboardInterrupt:
	webcam.destroy()
	cv2.destroyAllWindows()