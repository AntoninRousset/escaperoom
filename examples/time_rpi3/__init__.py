import cv2, os

from escaperoom import *

game = Game('time')
'''
def asdf():
    with open(fifo_path, 'wb', 0) as fifo:
        while True:
            ret, frame = cap.read()
            if ret == True:
                fifo.write(frame.tobytes())

from threading import Thread
thread = Thread(target=asdf)
thread.start()

from time import sleep
sleep(2)
'''
camera = LocalCamera('potions', '/dev/video0')
game.misc.add_camera(camera)

#TODO setup camera

import math, numpy
from PIL import ImageDraw
from av import VideoFrame

side = 8
xy = [ 
        ((math.cos(th) + 1) * 90, 
            (math.sin(th) + 1) * 60) 
        for th in [i * (2 * math.pi) / side for i in range(side)] 
        ] 

async def analyzer():
    while True:
        async with camera.video.frame_changed:
            frame = await camera.video.get_frame()
            image = frame.to_image()
            draw = ImageDraw.Draw(image)
            draw.polygon(xy, fill ="#eeeeff", outline ="blue")
            frame.planes[0].update(image.tobytes('raw'))

asyncio.create_task(analyzer())

