from asyncio import Lock
import logging


# - Failed to implement subscription weakref in event_subscriptions because
#   weakref was dead before subscription __aexit__ (aka before unregistering)

logger = logging.getLogger(__name__)


class EventSource:

    def __init__(self):
        self.event_subscriptions_lock = Lock()
        self.event_subscriptions = set()

    def subscribe(self):

        from .subscription import Subscription
        return Subscription(self)

    async def emit_event(self, event):

        from asyncio import gather

        async with self.event_subscriptions_lock:
            await gather(*(sub.emit_event(event)
                           for sub in self.event_subscriptions))

    async def register_subscription(self, sub):

        async with self.event_subscriptions_lock:
            self.event_subscriptions.add(sub)

    async def unregister_subscription(self, sub):

        async with self.event_subscriptions_lock:
            self.event_subscriptions.remove(sub)
