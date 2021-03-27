# CITATION
# Title: Drowsiness Detection
# Author: Konstantinos Thanos
# Date: 2021
# Availability: https://github.com/kostasthanos/Drowsiness-Detection
# followed this github's general format with some tweaks to add video file processing
# /CITATION

# Import packages
from scipy.spatial import distance as dist
import numpy as np
import dlib
import cv2

'''
Eye Aspect Ratio (E.A.R.)
Function to calculate eye aspect ratio as in paper :
"Real-Time Eye Blink Detection using Facial Landmarks [Soukupova, Cech]"
Landmarks |   0  1  2  3  4  5
 Left Eye : [36,37,38,39,40,41]
Right Eye : [42,43,44,45,46,47]
'''


def eye_aspect_ratio(eye):
    # Vertical distances
    dist1 = dist.euclidean(eye[1], eye[5])  # P2-P6
    dist2 = dist.euclidean(eye[2], eye[4])  # P3-P5
    # Horizontal distance
    dist3 = dist.euclidean(eye[0], eye[3])  # P1-P4
    # Eye Aspect Ratio (E.A.R.)
    ear = (dist1 + dist2) / (2.0 * dist3)

    return ear


'''
Lips Aspect Ratio (L.A.R.)
Function to calculate lips aspect ratio in the same way as in E.A.R.
Landmarks |   0  1  2  3  4  5  6  7
     Lips : [60,61,62,63,64,65,66,67]
'''


def lips_aspect_ratio(lips):
    # Vertical distance
    dist1 = dist.euclidean(lips[2], lips[6])  # L3-L7
    # Horizontal distance
    dist2 = dist.euclidean(lips[0], lips[4])  # L1-L5
    # Lips Aspect Ratio (L.A.R.)
    lar = float(dist1 / dist2)

    return lar


'''
Facial Landmarks for any face part
Function to calculate facial landmark point coordinates (x,y),
draw them on frame and return a numpy array with the corresponding points
'''


def draw_landmarks(face_part, landmarks,frame):
    landmarks_list = []
    start_frame = frame
    for point in face_part:
        x, y = landmarks.part(point).x, landmarks.part(point).y
        landmarks_list.append([x, y])
        cv2.circle(frame, (x, y), 2, (0, 0, 255), -1)
    return np.array(landmarks_list)



def main(source = None):
    def analyze_frame(frame):
        print('analyze')
        blinking = False
        yawning = False
        # Grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the gray frame
        faces = detector(gray, 0)

        # Loop through each face
        for face in faces:
            # Determine facial landmarks
            facial_landmarks = predictor(gray, face)

            # Landmark indexes for eyes and lips
            left_eye = [36, 37, 38, 39, 40, 41]
            right_eye = [42, 43, 44, 45, 46, 47]

            lips = [60, 61, 62, 63, 64, 65, 66, 67]

            # Convert to numpy array the above lists and
            # draw the corresponding facial landmark points on frame
            left_eye_points = draw_landmarks(left_eye, facial_landmarks,frame)
            right_eye_points = draw_landmarks(right_eye, facial_landmarks,frame)
            lips_points = draw_landmarks(lips, facial_landmarks,frame)

            # Find and draw the convex hulls of left and right eye, and lips
            left_eye_hull = cv2.convexHull(left_eye_points)
            cv2.drawContours(frame, [left_eye_hull], -1, (0, 255, 0), 1)

            right_eye_hull = cv2.convexHull(right_eye_points)
            cv2.drawContours(frame, [right_eye_hull], -1, (0, 255, 0), 1)

            lips_hull = cv2.convexHull(lips_points)
            cv2.drawContours(frame, [lips_hull], -1, (0, 255, 0), 1)

            # Calculate E.A.R. and L.A.R.
            left_ear = eye_aspect_ratio(left_eye_points)  # Left eye aspect ratio
            right_ear = eye_aspect_ratio(right_eye_points)  # Right eye aspect ratio

            ear = (left_ear + right_ear) / 2.0  # Average eye aspect ratio

            lar = lips_aspect_ratio(lips_points)  # Lips aspect ratio

            if ear < ear_thresh:
                blinking = True
            if lar > lar_thresh:
                yawning = True
        return (blinking, yawning)

    # DLIB - Face Detector and Predictor
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

    # Initializations
    frames = 0

    # e.a.r & l.a.r, threshold values
    ear_thresh = 0.3
    lar_thresh = 0.5

    # Blink initializations
    blink_counter, total_blinks = 0, 0
    # Yawn initializations
    yawn_counter, total_yawns = 0, 0

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.7

    #if no source, we use live video capture
    if not source:
        # Video Capture
        cap = cv2.VideoCapture(0)

        while True:
            _, frame = cap.read()
            frame = cv2.flip(frame, 1)  # May not be necessary
            h, w = frame.shape[: 2]  # Height and Width of frame

            frames += 1

            blinking, yawning = analyze_frame(frame)

            #cv2.putText(frame, "L.A.R. : {:.2f}".format(lar), (10, 90), font, font_scale, (0, 0, 255), 2)
            #cv2.putText(frame, "L.A.R. : {:.2f}".format(ear), (10, 90), font, font_scale, (0, 0, 255), 2)


            if blinking:
                blink_counter += 1
            else:
                if blink_counter > 1:
                    total_blinks += 1
                blink_counter = 0
            cv2.putText(frame, "Blinks: {}".format(total_blinks), (10, 50), font, font_scale, (0, 0, 255), 2)
            # YAWN detected
            if yawning:
                yawn_counter += 1
            else:
                if yawn_counter > 1:
                    total_yawns += 1
                yawn_counter = 0
            cv2.putText(frame, "Yawns: {}".format(total_yawns), (10, 110), font, font_scale, (0, 0, 255), 2)
            cv2.imshow('Frame', frame)
            key = cv2.waitKey(1)
            # if the user presses the 'esc' key, quit out
            if key == 27:
                break
        cap.release()
        cv2.destroyAllWindows()

    if source:
        pass


if __name__ == '__main__':
    main()
