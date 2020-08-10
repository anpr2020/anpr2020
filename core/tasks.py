from celery.decorators import task

#project imports start
import os
import re
import cv2
import random
import imutils
import Levenshtein
import pytesseract
import numpy as np
import pandas as pd
from io import BytesIO
from django.core.files.storage import default_storage
#project import end

INP_REGEX = r'^[A-Z]{2}\s*[0-9]{1,2}\s*[A-Z]{1,2}\s*[0-9]{1,4}$'

def get_result_plates(all_texts):
    found_plates = []
    all_plates = []
    grouped_plates = []
    #Merge inner lists
    for texts in all_texts:
        for text in texts:
            all_plates.append(text)

    #Group Plates
    len_plates = len(all_plates)
    for i in range(len_plates):
        group_plates = {}
        plate = all_plates[i]
        for j in range(len_plates):
            plate2 = all_plates[j]
            if i!=j:
                r = Levenshtein.ratio(plate, plate2)
                if plate in group_plates:
                    group_plates[plate] += 1
                elif r > 0.85:
                    group_plates[plate2] = 1

        grouped_plates.append(group_plates)


    for group_plates in grouped_plates:
        if not group_plates:
            continue
        max_found_plate, max_count = list(group_plates.items())[0]
        for pk, pv in group_plates.items():
            if pv > max_count:
                max_found_plate, max_count = pk, pv

        if max_found_plate not in found_plates:
            found_plates.append(max_found_plate)

    return found_plates

def remove_duplicates(texts):
    nd_texts = []
    for t in texts:
        t = t.upper()
        if t not in nd_texts:
            nd_texts.append(t)
    return nd_texts

def filter_pnames(texts):
    new_texts = []
    texts = remove_duplicates([''.join(t.split()) for t in texts])
    len_texts = len(texts)
    for i in range(len_texts):
        f = False
        for j in range(len_texts):
            if i!=j:
                r = Levenshtein.ratio(texts[i], texts[j])
                if r > 0.75:
                    f = True

        if not f:
            new_texts.append(texts[i])

    return new_texts

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
    return ''.join([char for char in text if (char.isupper() or char.isdigit()) and char.upper() in include]).strip()

def frame_process(success, frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    canny_output = cv2.Canny(gray, 170, 200)

    contours, hierarchy = cv2.findContours(
        canny_output, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    plate_match, rec_texts = False, []
    for contour in contours:
        approx = cv2.approxPolyDP(
            contour, cv2.arcLength(contour, True) * 0.05, True)

        if len(approx) >= 4 and np.abs(cv2.contourArea(contour)) > 1000:
            rect = cv2.minAreaRect(contour)
            box = np.int0(cv2.boxPoints(rect))
            (box_w, box_h) = helper_boxwh(box)

            #https://orbiz.in/number-plate-rules-in-india/
            accepted_ratios = [1.7, 2, 4.16]
            error = 0.82

            ratio = box_w / box_h

            for accepted_ratio in accepted_ratios:
                if accepted_ratio - error < ratio and ratio < accepted_ratio + error:
                    plate_match = True
                    x, y, w, h = cv2.boundingRect(approx)
                    plate_frame = frame[y:y+h,x:x+w]
                    rec_text = get_text_from_frame(plate_frame.copy())

                    if not re.match(INP_REGEX, rec_text):
                        continue
                    rec_texts.append(rec_text)

                    cv2.drawContours(
                        frame, [box, contour, approx], 2, (0, 0, 255), 5)
                    cv2.putText(frame, rec_text, (x, y),
                                cv2.FONT_HERSHEY_SIMPLEX , 1.5, (0, 255, 0), 2, cv2.LINE_AA)

    drawing = np.zeros(
        (canny_output.shape[0], canny_output.shape[1], 3), dtype=np.uint8)

    for contour in contours:
        color = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
        cv2.drawContours(drawing, contour, -1, color)

    plate = frame.copy()

    return canny_output, drawing, plate, rec_texts, plate_match

@task(bind=True)
def recognize_live(self, video_path):
    pass #future implemented

@task(bind=True)
def recognize(self, video_path):

    task_id = self.request.id
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

    def info_append(k, v, type=1, fnum=0):
        if type == 1:
            path = os.path.join(task_id, k, '{}.jpg'.format(str(fnum).zfill(3)))
            v = 'http://127.0.0.1:8000/media/' + default_storage.save(path, BytesIO(cv2.imencode('.jpg', v)[1].tobytes()))
        info_data[k].append(v)

    success, frame = video_cap.read()
    all_rec_texts = []
    while success:
        total += 1
        original_frame = frame.copy()
        canny_output, drawing, plate, rec_texts, plate_match = frame_process(success, frame)

        rec_texts = remove_duplicates(rec_texts)
        info_append('frame', original_frame, fnum=total)
        info_append('canny', canny_output, fnum=total)
        info_append('contour', drawing, fnum=total)
        info_append('plate', plate, fnum=total)
        info_append('text', rec_texts, 0)

        if plate_match:
            count += 1

        all_rec_texts.append(rec_texts)
        self.update_state(state="RUNNING", meta=info_data)
        success, frame = video_cap.read()

    video_cap.release()
    info_append('platesFound', get_result_plates(all_rec_texts), 0)

    return info_data
