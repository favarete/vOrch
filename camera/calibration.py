import numpy as np
import cv2
from pathlib import Path

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((6*7,3), np.float32)
objp[:,:2] = np.mgrid[0:7,0:6].T.reshape(-1,2)

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

pwd = Path.cwd() / "calibration_data" / "pattern" / "chessboard"

data_path = pwd / "calibration_ouput"
images_path = pwd / "img"

images = images_path.glob('*.jpg')

for fname in images:
    img = cv2.imread(str(fname))
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(gray, (7,6),None)

    # If found, add object points, image points (after refining them)
    if ret == True:
        objpoints.append(objp)

        corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)

        # Double check if everything's okay
        if type(corners2) is np.ndarray:
            imgpoints.append(corners2)

            # Draw and display the corners
            img = cv2.drawChessboardCorners(img, (7,6), corners2,ret)
            cv2.imshow('img',img)
            cv2.waitKey(500)

# Calibrate webcam and save output
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
np.savez(str(data_path), ret=ret, mtx=mtx, dist=dist, rvecs=rvecs, tvecs=tvecs)

# Re-projection Error (this should be as close to zero as possible)
mean_error = 0
for i in xrange(len(objpoints)):
    imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
    error = cv2.norm(imgpoints[i],imgpoints2, cv2.NORM_L2)/len(imgpoints2)
    mean_error += error

print "Total error: ", mean_error/len(objpoints)

cv2.destroyAllWindows()