from django.urls import path
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

from core import routing as croute

application = ProtocolTypeRouter({
    'websocket': URLRouter(
        croute.websocket_urlpatterns
    ),
})
