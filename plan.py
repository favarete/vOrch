from planner import pyhop
from utils import *

import numpy as np

state = pyhop.State("state")

def make_plan(number_of_robots, robots_data, task_manager):
	state.robots_available = number_of_robots

def nearby_points(movable_points, target_points):
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

def rotate_robot(movable_points, associated_target):
	result = {}
	for key, value in movable_points.iteritems():
		result[key] = angle_to_target(value["node"][0], value["node"][1], associated_target[key])
	return result

