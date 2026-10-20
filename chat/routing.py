from django.urls import re_path, path
from . import consumers


websocket_urlpatterns= [
    re_path(r'ws/chat/(?P<conversation_id>\d+)/$', consumers.ConversationConsumer.as_asgi()),
    path("ws/notifications/", consumers.NotificationConsumer.as_asgi()),
    path("ws/presence/", consumers.PresenceConsumer.as_asgi()),
]