import json
import time
from channels.generic.websocket import AsyncWebsocketConsumer

from celery.result import AsyncResult
from core.tasks import recognize

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.task_name = self.scope['url_route']['kwargs']['task_id']
        self.t = AsyncResult(self.task_name)
        self.task_group_name = 'chat_%s' % self.task_name

        # await self.channel_layer.group_add(
        #     self.task_group_name,
        #     self.channel_name
        # )

        await self.accept()

    async def disconnect(self, close_code):
        # await self.channel_layer.group_discard(
        #     self.task_group_name,
        #     self.channel_name
        # )
        pass

    async def receive(self, text_data):
        if 'ready' in text_data:
            t = self.t
            task_state, task_info = t.state, t.info

            if issubclass(type(task_info), Exception):
                task_info = str(task_info)

            await self.send(text_data=json.dumps({
                    'state': task_state,
                    'info': task_info
                }))
