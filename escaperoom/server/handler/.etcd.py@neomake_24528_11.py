import logging
from .base import WebHandler


LOGGER = logging.getLogger(__name__)


class EtcdHandler(WebHandler):

    def __init__(self, context, rootdir):

        super().__init__(context, rootdir)
        self.app.router.add_get('/tree/{selector:.*}', self.get_tree)

    async def get_tree(self, request):

        from . import to_json
        from aiohttp.web import Response

        selector = request.match_info['selector']
        tree = [key async for key in (self.context.etcd.root / selector).keys]

        return Response(content_type='application/json',
                        text=to_json(tree))
