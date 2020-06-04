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

def get_result_plates(texts):
    found_plates = []
    for t in texts:
        t = t.upper()
        if t not in found_plates:
            found_plates.append(t)

def remove_duplicates(texts):
    purified_texts = []
    for t in texts:
        t = t.upper()
        if t not in purified_texts:
            purified_texts.append(t)

    return purified_texts

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

def get_text_from_frame(frame):
    include = [char for char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890']
    text = pytesseract.image_to_string(frame, lang='eng')
    return ''.join([char for char in text if (char.isupper() or char.isdigit()) and char.upper() in include])

def frame_process(success, frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    canny_output = cv2.Canny(gray, 170, 200)

    contours, hierarchy = cv2.findContours(
        canny_output, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    plate_match = False
    rec_texts = []
    for contour in contours:
        approx = cv2.approxPolyDP(
            contour, cv2.arcLength(contour, True) * 0.05, True)

        if len(approx) >= 4 and np.abs(cv2.contourArea(contour)) > 2000:
            rect = cv2.minAreaRect(contour)
            box = np.int0(cv2.boxPoints(rect))
            (box_w, box_h) = helper_boxwh(box)

            #https://orbiz.in/number-plate-rules-in-india/
            accepted_ratios = [1.7, 2, 4.16]
            error = 0.6

            ratio = box_w / box_h

            for accepted_ratio in accepted_ratios:
                if accepted_ratio - error < ratio and ratio < accepted_ratio + error:
                    plate_match = True
                    x, y, w, h = cv2.boundingRect(approx)
                    plate_frame = frame[y:y+h,x:x+w]
                    plate_frame = cv2.cvtColor(plate_frame, cv2.COLOR_BGR2GRAY)
                    rec_text = get_text_from_frame(plate_frame.copy())
                    if not rec_text or len(rec_text) > 10:
                        continue
                    cv2.drawContours(
                        frame, [box, contour, approx], 2, (0, 0, 255), 5)
                    cv2.putText(frame, rec_text, (x, y),
                                cv2.FONT_HERSHEY_SIMPLEX , 1.5, (0, 255, 0), 2, cv2.LINE_AA)
                    info_append('text', rec_text, 0)
                    break

    if not plate_match:
        return None, None, None, None, None
    count += 1

    drawing = np.zeros(
        (canny_output.shape[0], canny_output.shape[1], 3), dtype=np.uint8)

    for contour in contours:
        color = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
        cv2.drawContours(drawing, contour, -1, color)

    plate = frame.copy()

    return canny_output, drawing, plate, rec_texts, plate_match

@task(bind=True)
def recognize_live(self, video_path):
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

    success, frame = video_cap.read()
    while success:
        total += 1
        canny_output, drawing, plate, rec_texts, plate_match = frame_process(success, frame.copy())
        if not rec_texts:
            continue
        info_append('frame', frame)
        info_append('canny', canny_output)
        info_append('contour', drawing)
        info_append('plate', plate)
        info_append('text', rec_texts, 0)

        if plate_match:
            count += 1

        self.update_state(state="RUNNING", meta=info_data)
        success, frame = video_cap.read()

    return info_data

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

    total = count = 0
    info_data = {
        'frame': [],
        'canny': [],
        'contour': [],
        'plate': [],
        'text': [],
        'platesFound': [],
    }

    def info_append(k, v, type=1):
        if type == 1:
            v = 'data:image/jpeg;base64,' + base64.b64encode(cv2.imencode('.jpg', v)[1]).decode("utf-8")
        info_data[k].append(v)

    success, frame = video_cap.read()

    while success:
        total += 1
        original_frame = frame.copy()
        canny_output, drawing, plate, rec_texts, plate_match = frame_process(success, frame)
        if not rec_texts:
            continue
        info_append('frame', original_frame)
        info_append('canny', canny_output)
        info_append('contour', drawing)
        info_append('plate', plate)
        info_append('text', remove_duplicates(rec_texts), 0)

        if plate_match:
            count += 1

        self.update_state(state="RUNNING", meta=info_data)
        success, frame = video_cap.read()

    video_cap.release()

    return info_data
