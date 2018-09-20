from utils import *
import numpy as np
from threading import Thread
import _global_

def run_planner():
	if _global_.task_manager["solve_task"] and _global_.task_manager["available_robot"]:
		if not _global_.task_manager["busy"]:
			_global_.task_manager["busy"] = True
			plan = make_plan()
			_global_.gui_properties["section_4"]["plan"] = plan
			print plan
			for r in plan:
				if len(plan[r]) > 0:
					Thread(target=_global_.robots_manager[r]["hardware"].run_plan, 
						   args=(plan[r], 
						   _global_.robots_manager)).start()
		else:
			check = all(value["running_plan"] == False for key, value in _global_.robots_manager.iteritems())
			if check:
				_global_.task_manager["busy"] = False
				_global_.task_manager["solve_task"] = False
				print "All plans executed!"
				_global_.gui_properties["section_4"]["plan"] = None
			pass


def make_plan():
	plan = {}
	nearby_points = aux_nearby_points(_global_.robots_manager, _global_.task_manager["solution_points"])
	needed_rotation = aux_rotate_robots(_global_.robots_manager, nearby_points)

	for element in _global_.robots_manager:
		if element in needed_rotation:
			plan[element] = []
			if needed_rotation[element] >= _global_.gui_properties["section_2"]["variable_errorr"]:
				plan[element].append(("rotateLeft", np.absolute(needed_rotation[element]) ))
			elif needed_rotation[element] < -_global_.gui_properties["section_2"]["variable_errorr"]:
				plan[element].append(("rotateRight", np.absolute(needed_rotation[element]) ))

			ru_distance = get_ru_distance(nearby_points[element], 
										  _global_.robots_manager[element]["node"][0], 
										  _global_.robots_manager[element]['radius'] * 2)
			if ru_distance > _global_.gui_properties["section_2"]["variable_errord"]:
				plan[element].append(("moveForward", ru_distance))
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