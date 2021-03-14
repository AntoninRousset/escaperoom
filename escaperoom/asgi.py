"""
ASGI config for escaperoom project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter
from django.core.asgi import get_asgi_application

from .handlers import LifespanHandler

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'escaperoom.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'lifespan': LifespanHandler
})
