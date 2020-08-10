import os
import json
from django.shortcuts import render
from django.http import Http404, JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.core.files.storage import default_storage

from celery.result import AsyncResult
from .tasks import recognize
#project import end

@csrf_exempt
@never_cache
def progress(request):
    print(request.method)
    if request.method == 'POST':
        jobj = json.loads(request.body.decode('utf-8'))
        task_id = jobj.get('task_id')
        t = AsyncResult(task_id)
        state, info = t.state, t.info
        if issubclass(type(t.info), Exception):
            info = str(t.info)
        return JsonResponse({'state': state, 'info': info})
    return Http404

@csrf_exempt
def recognition(request):
    try:
        if request.method == 'POST' and request.FILES:
            video_file = request.FILES.get('video_file')

            if not video_file:
                raise Exception

            file_name = default_storage.save(video_file.name, video_file)
            video_path = os.path.join(settings.MEDIA_ROOT, file_name)

            t_id = recognize.delay(video_path).task_id
            return JsonResponse({'task_id': t_id})
    except Exception as e:
        print(e)
    raise Http404
