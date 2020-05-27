import cv2
from aiohttp import web


class Video:

    def __init__(self, path):
        self._path = path

    async def get_frames(self):
        pass


def frames(path):
    camera = cv2.VideoCapture(path)
    if not camera.isOpened():
        raise RuntimeError('Cannot open camera')

    while True:
        _, img = camera.read()
        img = cv2.resize(img, (480, 320))
        frame = cv2.imencode('.jpg', img)[1].tobytes()
        yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n'+frame+b'\r\n'


routes = web.RouteTableDef()


@routes.get('/')
async def index(request):
    return web.FileResponse(f'/tmp/streaming.html')


@routes.get('/video_feed')
async def video_feed(request):
    response = web.StreamResponse()
    response.content_type = 'multipart/x-mixed-replace; boundary=frame'
    await response.prepare(request)
    for frame in frames('/dev/video0'):
        await response.write(frame)
    return response


app = web.Application()
app.add_routes(routes)
web.run_app(app)
