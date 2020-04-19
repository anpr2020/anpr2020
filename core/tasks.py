from celery.decorators import task

from django.conf import settings

#project imports start
import os
import re
import sys
import cv2
import shutil
import random
import base64
import imutils
import numpy as np
import pandas as pd
import pytesseract
import matplotlib.pyplot as plt
from imutils.object_detection import non_max_suppression
#project import end

@task(bind=True)
def recognize(self, video_path):

    t_loc, t_locs = None, [
        os.path.join('C:' + os.path.sep, 'Program Files', 'Tesseract-OCR', 'tesseract.exe'),
        os.path.join('C:' + os.path.sep, 'Program Files (x86)', 'Tesseract-OCR', 'tesseract.exe')
    ]
    for loc in t_locs:
        if os.path.exists(loc):
            t_loc = loc

    if not t_loc:
        return self.update_state(state='FAILURE', meta={'message': 'Tesseract location error'})

    pytesseract.pytesseract.tesseract_cmd = t_loc

    self.update_state(state='RUNNING')

    video_cap = cv2.VideoCapture(video_path)
    success, frame = video_cap.read()

    def get_text_from_frame(frame):
        include = [char for char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890']
        text = pytesseract.image_to_string(frame, lang='eng')
        return ''.join([char for char in text if (char.isupper() or char.isdigit()) and char.upper() in include])

    def helper_boxwh(box):
        x1 = box[0][0]
        y1 = box[0][1]
        x2 = box[1][0]
        y2 = box[1][1]
        x3 = box[2][0]
        y3 = box[2][1]

        w = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        h = np.sqrt((x3 - x2) ** 2 + (y3 - y2) ** 2)

        if np.abs(y2 - y1) < np.abs(y3 - y2):
            return (w, h)
        else:
            return (h, w)

    total = count = 0
    info_data = {
        'frame': [],
        'canny': [],
        'contour': [],
        'plate': [],
        'text': [],
    }

    def info_append(k, v, type=1):
        if type == 1:
            v = 'data:image/jpeg;base64,' + base64.b64encode(cv2.imencode('.jpg', v)[1]).decode("utf-8")
        info_data[k].append(v)

    while success:
        total += 1
        info_append('frame', frame)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        canny_output = cv2.Canny(gray, 170, 200)
        info_append('canny', canny_output)

        contours, hierarchy = cv2.findContours(
            canny_output, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        contours = sorted(contours, key=cv2.contourArea, reverse=True)

        plate_match = False
        for contour in contours:
            approx = cv2.approxPolyDP(
                contour, cv2.arcLength(contour, True) * 0.05, True)

            if len(approx) >= 4 and np.abs(cv2.contourArea(contour)) > 2000:
                rect = cv2.minAreaRect(contour)
                box = np.int0(cv2.boxPoints(rect))
                (box_w, box_h) = helper_boxwh(box)

                accepted_ratio = 4.16
                error = 0.84

                ratio = box_w / box_h

                if accepted_ratio - error < ratio and ratio < accepted_ratio + error:
                    cv2.drawContours(
                        frame, [box, contour, approx], 2, (0, 0, 255), 5)
                    x, y, w, h = cv2.boundingRect(approx)
                    plate_frame = frame[y:y+h,x:x+w]
                    rec_text = get_text_from_frame(plate_frame)

                    if not rec_text:
                        continue

                    plate_match = True
                    cv2.putText(frame, rec_text, (x, y),
                                cv2.FONT_HERSHEY_SIMPLEX , 1.5, (0, 255, 0), 2, cv2.LINE_AA)
                    info_append('text', rec_text, 0)

        if plate_match:
            count += 1

        drawing = np.zeros(
            (canny_output.shape[0], canny_output.shape[1], 3), dtype=np.uint8)

        for contour in contours:
            color = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
            cv2.drawContours(drawing, contour, -1, color)

        info_append('contour', drawing)
        info_append('plate', frame)

        self.update_state(state="RUNNING", meta=info_data)

        success, frame = video_cap.read()

    video_cap.release()
