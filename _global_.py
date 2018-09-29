from database import SYSTEM_IDS
import numpy as np

server = None

gui_properties = {
	"section_1a": { 
					"filter_borders": False,
					"filter_gray": False,
					"filter_blur": False
	},

	"section_1b": {
					"detection_view": True,
					"all_squares_view": False
	},

	"section_2": {
					"variable_fps": 24,
					"variable_blur": 7,
					"variable_minsqr": 350,
					"variable_maxsqr": 120000,
					"variable_sqrdst": .4,
					"variable_cannyt": .7,
					"variable_errorr": 2,
					"variable_errord": .5
	},

	"section_3": {
					"server": False
	},

	"section_4": {
					"plan": None,
					"points": []
	}

}

robots_manager = { identification: {"node": np.empty((2, 2), dtype=int), 
									"radius": 0,
							 		"indetified": False,
							 		"hardware": None,
							 		"running_plan": False,
							 		"battery": "" } 
							 		for identification in SYSTEM_IDS[0] }

task_manager = {"solve_task": False,
				"busy": False,
				"task_ID": "",
				"solution_points":[],
				"solved_tasks": [],
				"available_robot": False,
				"busy_robots": 0  }