from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('ws/progress/<task_id>', consumers.ChatConsumer),
]
