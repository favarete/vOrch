#The pattern used must begin with the front pointed up and 
#turning clockwise: Front points Top -> Right -> Down -> Left
from utils import prepare_glyph

PATTERN = { "ID::0000": prepare_glyph([0, 1, 0, 0, 1, 0, 0, 0, 0]),
			"ID::0001": prepare_glyph([0, 0, 1, 1, 0, 1, 0, 0, 0])
}

TASK = { 
		 "ID::C": { "matrix": prepare_glyph([0, 1, 1, 1, 0, 0, 0, 1, 1]),
				    "difficult": 2,
				    "dimension": 200
				  },
		 "ID::A": { "matrix": prepare_glyph([1, 0, 0, 0, 1, 0, 1, 0, 1]),
				    "difficult": 1,
				    "dimension": 200
				  },

		 "ID::B": { "matrix": prepare_glyph([1, 1, 1, 0, 1, 0, 1, 1, 0]),
				    "difficult": 3,
				    "dimension": [140, 60, 120]
				  }
}

SYSTEM_IDS = (PATTERN.keys(), TASK.keys())