from database import SYSTEM_IDS
import numpy as np

gui_properties = {
	"section_1a": { 
					"filter_borders": False,
					"filter_gray": False,
					"filter_blur": False
	},

	"section_1b": {
					"detection_view": True,
					"all_squares_view": False
	}
}

robots_manager = { identification: {"node": np.empty((2, 2), dtype=int), 
									"radius": 0,
							 		"indetified": False,
							 		"running_plan": False } 
							 		for identification in SYSTEM_IDS[0] }

task_manager = {"solve_task": False,
				"busy": False,
				"task_ID": "",
				"solution_points":[],
				"solved_tasks": [],
				"busy_robots": 0  }