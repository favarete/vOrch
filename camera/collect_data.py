from webcam import Webcam
import cv2
import uuid
from pathlib import Path
  
camera = 1

chess_pattern_path = Path.cwd() / "calibration_data" / "pattern" / "chessboard" / "img"
if chess_pattern_path.exists() == False:
    chess_pattern_path.mkdir(parents=True)

webcam = Webcam(camera)
webcam.start()

try:
    while True:
        img = webcam.get_current_frame()
        cv2.imshow('capture', img)
        cv2.waitKey(500)
        
        ret, corners = cv2.findChessboardCorners(cv2.cvtColor(img,cv2.COLOR_BGR2GRAY), (7,6), None)
        
        if ret == True:
            filename = "sample" + str(uuid.uuid4().hex) + '.jpg'
            cv2.imwrite(str(chess_pattern_path / filename), img)

except KeyboardInterrupt:
    webcam.destroy()
    cv2.destroyAllWindows()