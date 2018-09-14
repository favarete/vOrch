#The pattern used must begin with the front pointed up and 
#turning clockwise: Front points Top -> Right -> Down -> Left

PATTERN = { "ID::0000": [
						[0, 1, 0, 0, 1, 0, 0, 0, 0],
				  		[0, 0, 0, 0, 1, 1, 0, 0, 0],
				  		[0, 0, 0, 0, 1, 0, 0, 1, 0],
				  		[0, 0, 0, 1, 1, 0, 0, 0, 0]
				  		]
}

TASK = { 
		 "ID::C": { "matrix":[
						[0, 1, 1, 1, 0, 0, 0, 1, 1],
				   		[0, 1, 0, 1, 0, 1, 1, 0, 1],
				   		[1, 1, 0, 0, 0, 1, 1, 1, 0],
				   		[1, 0, 1, 1, 0, 1, 0, 1, 0]
				  		],
				    "difficult": 2,
				    "dimension": 200
				  },
		 "ID::A": { "matrix":[
						[1, 0, 0, 0, 1, 0, 1, 0, 1],
				  		[1, 0, 1, 0, 1, 0, 1, 0, 0],
				  		[1, 0, 1, 0, 1, 0, 0, 0, 1],
				  		[0, 0, 1, 0, 1, 0, 1, 0, 1]
				   		],
				    "difficult": 1,
				    "dimension": 200
				  },

		 "ID::B": { "matrix":[
						[1, 1, 1, 0, 1, 0, 1, 1, 0],
				   		[1, 0, 1, 1, 1, 1, 0, 0, 1],
				   		[0, 1, 1, 0, 1, 0, 1, 1, 1],
				   		[1, 0, 0, 1, 1, 1, 1, 0, 1]
				   		],
				    "difficult": 3,
				    "dimension": [140, 60, 120]
				  }
}

SYSTEM_IDS = (PATTERN.keys(), TASK.keys())