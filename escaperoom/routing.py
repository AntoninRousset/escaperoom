from channels.routing import URLRouter
from django.urls import path
from network.routing import ws_urlpatterns as node_ws_urlpatterns


ws_urlpatterns = [
    path('api/network/', URLRouter(node_ws_urlpatterns))
]
