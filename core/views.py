from django.shortcuts import render
from django.http import Http404, JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

#project imports start
import cv2
import sys
import os
import re
import imutils
import shutil
import numpy as np
import pandas as pd
import pytesseract
from imutils.object_detection import non_max_suppression
import matplotlib.pyplot as plt
#project import end

def home(request):
    return render(request, 'home.html')

def select_video(request):
    return render(request, 'selectVideo.html')

@csrf_exempt
def recognition(request):
    if request.method == 'POST' and request.FILES:

        #Start project process
        frame_dir = os.path.join(settings.BASE_DIR, 'media', 'frames')
        if not os.path.exists(frame_dir):
            os.makedirs(frame_dir)
        else:
            shutil.rmtree(os.path.join('media', 'frames'))
            os.mkdir(frame_dir)

        file = request.FILES.get('video_file')
        fname = file.temporary_file_path()

        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

        def preprocess_frame(frame):
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blur = cv2.bilateralFilter(gray, 11, 17, 17)
            canny_edge = cv2.Canny(blur, 170, 200)

            (new, contours, _) = cv2.findContours(canny_edge.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            contours=sorted(contours, key = cv2.contourArea, reverse = True)[:30]
            plate_count = None
            status = False


            for c in contours:
                peri = cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, 0.02 * peri, True)
                if len(approx) == 4:
                    plate_count = approx
                    break

            if isinstance(plate_count,np.ndarray) :
                kernel = np.zeros(gray.shape,np.uint8)
                num_plt_image = cv2.drawContours(kernel,[plate_count],0,255,-1)
                num_plt_image = cv2.bitwise_and(frame,frame,mask=kernel)
                status = True
            else:
                num_plt_image = frame

            th, binary = cv2.threshold( num_plt_image, 127,255,cv2.THRESH_BINARY );
        # cv2.imwrite('binary.png',binary)
            return binary, status

        def convert2Frame(outDir, fname):
            vidcapture = cv2.VideoCapture(fname)
            success,image = vidcapture.read()
            count = 0
            if not os.path.exists(outDir):
                os.makedirs(outDir)
            while success:
                image, stat = preprocess_frame(imutils.rotate(image,-90))
                if stat == True:
                    cv2.imwrite(outDir+"\\%d.png" % count, image)
                success,image = vidcapture.read()
                count += 1
            return count

        frame_count = convert2Frame(frame_dir, fname)

        def get_text_from_frame(imgpath):
            image = cv2.imread(imgpath)
            text = pytesseract.image_to_string(image, config=('-l eng --oem 1 --psm 3'))
            return imgpath, text

        data, dict_count = [], {}
        for frame in range(frame_count):
            filename=str(frame)+".png"
            fname = os.path.join(settings.BASE_DIR, 'media', 'frames', filename)
            if os.path.isfile(fname):
                img_path, text = get_text_from_frame(fname)
                if len(text) > 8:
                    text = ''.join(e for e in text.strip() if e.isalnum())
                    if text in dict_count:
                        dict_count[text] += 1
                    else:
                        dict_count[text] = 1
                    data.append((filename, text))
        result = None
        max_count = 0
        re_card = r"^[a-zA-Z][a-zA-Z]\d\d[a-zA-Z][a-zA-Z]\d\d\d\d$"
        for k, v in dict_count.items():
            if v > max_count:
                result, max_count = k, v
        if result[2] in ['o', 'O']:
            result = result[:2] + '0' + result[3:]
        return JsonResponse({'data': data, 'result': result})
    raise Http404
