import cv2, os

from escaperoom import *

game = Game('time_rpi')

camera = LocalCamera('potions', '/dev/video0')

display = LocalDisplay('clues')

HTTPServer(port=8081)
