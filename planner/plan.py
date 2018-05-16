from utils import *
import numpy as np

ERROR = 5
#robots_available = {}

def make_plan(robots_data, task_manager):
	plan = {}
	nearby_points = aux_nearby_points(robots_data, task_manager["solution_points"])
	needed_rotation = aux_rotate_robots(robots_data, nearby_points)

	for element in robots_data:
		if element in needed_rotation:
			plan[element] = []
			if needed_rotation[element] >= 0:
				plan[element].append(("rotateLeft", np.absolute(needed_rotation[element]) ))
			else:
				plan[element].append(("rotateRight", np.absolute(needed_rotation[element]) ))

			plan[element].append(("moveForward", get_ru_distance(nearby_points[element], 
							  									 robots_data[element]["node"][0],
							  									 robots_data[element]['diameter'])))
	return plan
	
def aux_nearby_points(movable_points, target_points):
	result = {}
	data = movable_points.copy()
	if len(data) >= len(target_points):
		for point in target_points:
			M = float("inf")
			temp = ""
			for key, value in data.iteritems():
				distance = np.linalg.norm(point-value["node"][0])
				if distance < M:
					temp = key
					M = distance
			data.pop(temp, None)
			result[temp] = point
	return result

def aux_rotate_robots(movable_points, associated_target):
	result = {}
	for key, value in movable_points.iteritems():
		if key in associated_target:
			result[key] = angle_to_target(value["node"][0], value["node"][1], associated_target[key])
	return result

def free_way(state):
	pass

def imminent_collision(state):
	pass