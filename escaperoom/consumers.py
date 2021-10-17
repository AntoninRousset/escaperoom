import logging
from channels.consumer import AsyncConsumer
from channels.layers import get_channel_layer

channel_layer = get_channel_layer()
logger = logging.getLogger(__name__)


class LifespanConsumer(AsyncConsumer):

    async def lifespan_startup(self, message):
        await self.send({'type': 'lifespan.startup.complete'})

    async def lifespan_shutdown(self, message):
        await self.send({'type': 'lifespan.shutdown.complete'})
