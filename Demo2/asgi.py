"""
ASGI config for Demo2 project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""
print("asgi file running")
import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.security.websocket import AllowedHostsOriginValidator
# from channels.auth import AuthMiddlewareStack

from chat import routing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Demo2.settings')

application = ProtocolTypeRouter({
    'http':get_asgi_application(),
    #  "websocket": AllowedHostsOriginValidator(
    #     AuthMiddlewareStack(URLRouter(routing.websocket_urlpatterns))
    # ),

    "websocket":URLRouter(routing.websocket_urlpatterns),
})


