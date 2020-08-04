from asyncio import Lock
import logging


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

        # check for dead ref
        if (r() is None for r in self.event_subscriptions):
            logger.warning(f'Dead subscription reference(s) found in {self}, '
                           'cleaning up')
            await self.unregister_subscription(None)

        async with self.event_subscriptions_lock:
            await gather(*(r() and r().emit(event)
                           for r in self.event_subscriptions))

    async def register_subscription(self, sub):

        from weakref import ref

        async with self.event_subscriptions_lock:
            self.event_subscriptions.add(ref(sub))

    async def unregister_subscription(self, sub):

        async with self.event_subscriptions_lock:
            self.event_subscriptions = set(filter(lambda r: r() is not sub,
                                                  self.event_subscriptions))
