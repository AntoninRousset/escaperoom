from django.urls import path
from network import consumers


ws_urlpatterns = [
    path('node/<uuid:id>/', consumers.NodeConsumer.as_asgi())
]
