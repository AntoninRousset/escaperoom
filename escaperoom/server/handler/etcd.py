import logging
from .base import WebHandler


LOGGER = logging.getLogger(__name__)


class EtcdHandler(WebHandler):

    def __init__(self, context, rootdir):

        super().__init__(context, rootdir)
        self.app.router.add_get('/{selector:.*}', self.get_selector)
        self.add_event_source(self.context.etcd.root / '**')

    async def get_selector(self, request):

        from . import to_json
        from aiohttp.web import Response

        accessor = self.context.etcd.root / request.match_info['selector']

        with_values = ('with_values' in request.query)

        if 'list' in request.query:
            if with_values:
                data = {str(k): v async for k, v in accessor.items}
            else:
                data = {str(k): None async for k in accessor.keys}
        else:
            data = await accessor.instantiate(with_values=with_values)

        return Response(content_type='application/json',
                        text=to_json(data))
