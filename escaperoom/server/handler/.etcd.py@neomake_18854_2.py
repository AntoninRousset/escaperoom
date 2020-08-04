import logging
from .base import WebHandler


LOGGER = logging.getLogger(__name__)


class EtcdHandler(WebHandler):

    def __init__(self, context, rootdir):

        super().__init__(context, rootdir)
        self.app.router.add_get('/tree/{selector:.*}', self.get_selector)

    async def get_selector(self, request):

        from . import to_json
        from aiohttp.web import Response

        accessor = self.context.etcd.root / request.match_info['selector']
        with_values = ('with_values' in request.query)
        instance = await accessor.instantiate(with_values=with_values)

        return Response(content_type='application/json',
                        text=to_json(instance))
