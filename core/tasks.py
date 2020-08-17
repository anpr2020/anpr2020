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

def filter_pnames(texts):
    new_texts = []
    texts = list(dict.fromkeys([(''.join(t.split())).upper() for t in texts]))
    len_texts = len(texts)
    for i in range(len_texts):
        f = False
        for j in range(len_texts):
            if i!=j:
                r = Levenshtein.ratio(texts[i], texts[j])
                if r > 0.8:
                    f = True

        if not f:
            new_texts.append(texts[i])

    return new_texts

def get_grouped_plates(all_plates):
    grouped_plates = []
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
                elif r > 0.8:
                    group_plates[plate2] = 1

        grouped_plates.append(group_plates)

    return grouped_plates

def process_grouped_plates(grouped_plates):
    found_plates = {}
    for group_plates in grouped_plates:

        if not group_plates:
            continue

        group_items = group_plates.items()
        max_found_plate, max_count = list(group_items)[0]
        for pk, pv in group_items:
            if pv > max_count:
                max_found_plate, max_count = pk, pv

        if max_found_plate not in found_plates.keys():
            found_plates.update({max_found_plate: max_count})

    return found_plates

def final_process(found_plates):

    if len(found_plates) <= 1:
        return list(found_plates.keys())

    final_plates = []
    similar_found = True
    while similar_found and found_plates:
        flag = False
        max_plate = max(found_plates, key=found_plates.get)
        for plate, plate_count in list(found_plates.items()):
            r = Levenshtein.ratio(max_plate, plate)
            if 0.8 < r < 1:
                found_plates.pop(plate)
                flag |= True

        found_plates.pop(max_plate)
        final_plates.append(max_plate)

        similar_found = flag

    return final_plates

def get_result_plates(all_texts):
    all_plates = []
    #Merge inner lists
    for texts in all_texts:
        for text in texts:
            all_plates.append(text)

    grouped_plates = get_grouped_plates(all_plates)

    found_plates = process_grouped_plates(grouped_plates)

    return final_process(found_plates)

def get_text_from_frame(frame):
    include = [char for char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890']
    text = pytesseract.image_to_string(frame, lang='eng', config='--psm 11')
    return ''.join([char for char in text if (char.isupper() or char.isdigit()) and char.upper() in include]).strip()

def correct_angle(image, angle):
   (h, w) = image.shape[:2]
   center = (w / 2, h / 2)
   M = cv2.getRotationMatrix2D(center, angle, 1.0)
   rotated_image = cv2.warpAffine(image, M, (w,h))
   return rotated_image

def frame_process(success, frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 13, 15, 15)
    canny_output = cv2.Canny(gray, 170, 200)

    contours, hierarchy = cv2.findContours(
        canny_output, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:30]

    plate_match, rec_texts = False, []
    for contour in contours:
        approx = cv2.approxPolyDP(
            contour, cv2.arcLength(contour, True) * 0.018, True)

        if len(approx) >= 4 and np.abs(cv2.contourArea(contour)) > 1000:
            rect = cv2.minAreaRect(contour)
            box = np.int0(cv2.boxPoints(rect))
            x, y, w, h = cv2.boundingRect(approx)
            plate_frame = frame[y:y+h,x:x+w]
            plate_frame = correct_angle(plate_frame, rect[2])
            plate_frame = cv2.cvtColor(plate_frame, cv2.COLOR_BGR2GRAY)
            plate_frame = cv2.threshold(plate_frame, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
            kernel = np.ones((1,1), np.uint8)
            plate_frame = cv2.dilate(plate_frame, kernel, iterations = 3)
            rec_text = get_text_from_frame(plate_frame.copy())
            if not re.match(INP_REGEX, rec_text):
                continue
            rec_texts.append(rec_text)
            plate_match = True

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
