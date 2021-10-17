import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from escaperoom import consumers, routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'escaperoom.settings')
http_app = get_asgi_application()

application = ProtocolTypeRouter({
    'http': http_app,
    'lifespan': consumers.LifespanConsumer(),
    'websocket': AuthMiddlewareStack(URLRouter(routing.ws_urlpatterns)),
})
