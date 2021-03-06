import cv2
import numpy as np
import _global_

def order_points(points):
 
	s = points.sum(axis=1)
	diff = np.diff(points, axis=1)
     
	ordered_points = np.zeros((4,2), dtype="float32")
 
	ordered_points[0] = points[np.argmin(s)]
	ordered_points[2] = points[np.argmax(s)]
	ordered_points[1] = points[np.argmin(diff)]
	ordered_points[3] = points[np.argmax(diff)]
 
	return ordered_points

def topdown_points(max_width, max_height):

	return np.array([
		[0, 0],
		[max_width-1, 0],
		[max_width-1, max_height-1],
		[0, max_height-1]], dtype="float32")

def get_topdown_quad(image, src):
 
	src = order_points(src)
 
	(max_width,max_height) = max_width_height(src)
	dst = topdown_points(max_width, max_height)
  
	matrix = cv2.getPerspectiveTransform(src, dst)
	warped = cv2.warpPerspective(image, matrix, max_width_height(src))
 
	return src, warped

def max_width_height(points):
 
	(tl, tr, br, bl) = points
 
	top_width = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
	bottom_width = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
	max_width = max(int(top_width), int(bottom_width))
 
	left_height = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
	right_height = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
	max_height = max(int(left_height), int(right_height))
 
	return (max_width,max_height)

def resize_image(image, new_size):

    ratio = new_size / image.shape[1]
    return cv2.resize(image,(int(new_size),int(image.shape[0]*ratio)))

def get_glyph_pattern(image):
 
    # collect pixel from each cell (left to right, top to bottom)
    cells = []
     
    cell_half_width = int(round(image.shape[1] / 10.0))
    cell_half_height = int(round(image.shape[0] / 10.0))

    blur_pattern = cv2.GaussianBlur(image,(5,5),0)
    ret, mask = cv2.threshold(blur_pattern, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
 
    row1 = cell_half_height*3
    row2 = cell_half_height*5
    row3 = cell_half_height*7
    col1 = cell_half_width*3
    col2 = cell_half_width*5
    col3 = cell_half_width*7

    cells.append(mask[row1, col1])
    cells.append(mask[row1, col2])
    cells.append(mask[row1, col3])
    cells.append(mask[row2, col1])
    cells.append(mask[row2, col2])
    cells.append(mask[row2, col3])
    cells.append(mask[row3, col1])
    cells.append(mask[row3, col2])
    cells.append(mask[row3, col3])
 
    # threshold pixels to either black or white
    for idx, val in enumerate(cells):
        if val == 0:
            cells[idx] = 0
        elif val == 255:
            cells[idx] = 1
        else:
            return None
 
    return cells

def is_valid_square(points, distortion):

	distortion = [np.subtract(1, distortion), np.add(1, distortion)]
	
	if len(points) != 4:
		return False

	area = cv2.contourArea(points)
	if area <= _global_.gui_properties["section_2"]["variable_minsqr"]:
		return False

	if area >= _global_.gui_properties["section_2"]["variable_maxsqr"]:
		return False

	if cv2.isContourConvex(points) == False:
		return False

	x,y,w,h = cv2.boundingRect(points)
	aspect_ratio = np.divide(float(w),h)

	if aspect_ratio < distortion[0] or aspect_ratio > distortion[1]:
		return False

	return True

def get_pattern_front(id, points):

	front_robot = [(0, 1), (1, 2), (2, 3), (3, 0)]	

	edge = front_robot[id]

	a = points[edge[0]]
	b = points[edge[1]]

	frontX = int(np.divide(np.add(a[0], b[0]), 2))
	frontY = int(np.divide(np.add(a[1], b[1]), 2))

	return frontX, frontY

def get_central_points(contour):

	M = cv2.moments(contour)
	x = int( np.divide(M["m10"], np.add(M["m00"], 1.0) ))
	y = int( np.divide(M["m01"], np.add(M["m00"], 1.0) ))

	return x, y

def get_euclidean_distance(x1, y1, x2, y2):

	return np.sqrt( np.add(np.square(np.subtract(x2, x1)), np.square(np.subtract(y1, y2))) )

def get_ru_distance(central1, central2, DIAMETER):

	ERROR = .1

	euclidean_dist = get_euclidean_distance(central1[0], central1[1], central2[0], central2[1])

	robotic_units = np.subtract(np.divide(euclidean_dist, DIAMETER), ERROR)

	return np.around(robotic_units, decimals=1)

def get_extended_point(x1, y1, x2, y2, dist):
	
	AB = get_euclidean_distance(x1, y1, x2, y2)

	X = np.add(x1, np.multiply(dist, ( np.divide(np.subtract(x2, x1), AB) )))
	Y = np.add(y1, np.multiply(dist, ( np.divide(np.subtract(y2, y1), AB) )))

	if type(X) != np.float64 or type(Y) != np.float64:
		return x1, y1

	return int(X), int(Y)

def get_perpendicular_points(x1, y1, x2, y2):

	xa = int( np.add( np.negative(np.subtract(y2, y1)), x1 ))
	ya = int( np.add( np.subtract(x2, x1), y1 ))
	xb = int( np.add( np.subtract(y2, y1), x1) )
	yb = int( np.add( np.subtract(x1, x2), y1) )

	return xa, ya, xb, yb

def angle_to_target(common, front, target):

	frontAngle = np.rad2deg( np.arctan2( np.subtract(front[1], common[1]), np.subtract(front[0], common[0]) ))
	targetAngle = np.rad2deg( np.arctan2( np.subtract(target[1], common[1]), np.subtract(target[0], common[0]) ))

	totalAngle = np.subtract(frontAngle, targetAngle)

	if totalAngle >= 180.0:
		return int(np.subtract(totalAngle, 360.0))

	if totalAngle <= -180.0:
		return int(np.add(totalAngle, 360.0))

	return int(totalAngle)

def is_intersecting(centerX1, centerY1, centerX2, centerY2, THRESHOLD):

	dist = get_euclidean_distance(centerX1, centerY1, centerX2, centerY2)

	if dist <= THRESHOLD:
		return True
	return False

def get_collision_points(centerX1, centerY1, centerX2, centerY2, RADIUS):

	dist = get_euclidean_distance(centerX1, centerY1, centerX2, centerY2)
	h = np.sqrt( np.subtract(np.square(RADIUS), np.square(np.divide(dist, 2.0))) )

	centerIntersectionX = np.divide(np.add(centerX1, centerX2), 2.0)
	centerIntersectionY = np.divide(np.add(centerY1, centerY2), 2.0)

	interX1 = np.add( centerIntersectionX, np.divide( np.multiply(np.subtract(centerY1, centerY2), h), dist ) )
	interX2 = np.subtract( centerIntersectionX, np.divide( np.multiply(np.subtract(centerY1, centerY2), h), dist ) )
	interY1 = np.subtract( centerIntersectionY, np.divide( np.multiply(np.subtract(centerX1, centerX2), h), dist ) )
	interY2 = np.add( centerIntersectionY, np.divide( np.multiply(np.subtract(centerX1, centerX2), h), dist ) )

	return interX1, interX2, interY1, interY2

def get_polyline_list(points):
	
	new_list = np.array([[points[i],points[i+1]] for i in range(0,len(points),2)])
	return new_list

def circle_intersection(circle1, circle2):
	x1,y1,r1 = circle1
	x2,y2,r2 = circle2

	dx,dy = x2-x1,y2-y1
	d = np.sqrt(dx*dx+dy*dy)
	if d > r1+r2 or d < np.abs(r1-r2) or (d == 0 and r1 == r2):
		return None 

	a = (r1*r1-r2*r2+d*d)/(2*d)
	h = np.sqrt(r1*r1-a*a)
	xm = x1 + a*dx/d
	ym = y1 + a*dy/d
	xs1 = int(xm + h*dy/d)
	xs2 = int(xm - h*dy/d)
	ys1 = int(ym - h*dx/d)
	ys2 = int(ym + h*dx/d)

	return (xs1,ys1),(xs2,ys2)


def get_midpoint(p1, p2):
	x = int((p1[0] + p2[0])/2)
	y = int((p1[1] + p2[1])/2)
	return (x, y)

def rotate_around_point(origin, point, angle):
	
	if angle < 0:
		angle += 360
	radians = np.deg2rad(angle*-1)
	x0, y0 = point
	xc, yc = origin

	qx = (x0 - xc) * np.cos(radians) - (y0 - yc) * np.sin(radians) + xc
	qy = (x0 - xc) * np.sin(radians) + (y0 - yc) * np.cos(radians) + yc

	return [qx, qy]

def prepare_glyph(code):
    glyph = [code]
    glyph_pos = code
    for i in range(3):
        mat = np.reshape(glyph_pos,(3,-1))
        glyph_pos = np.reshape(np.rot90(mat, 3),(-1,)).tolist()
        glyph.append(glyph_pos)
    return glyph