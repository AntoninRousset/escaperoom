#!/usr/bin/env python

'''
 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, version 3.
 This program is distributed in the hope that it will be useful, but
 WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 General Public License for more details.
 You should have received a copy of the GNU General Public License
 along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

import cv2
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation
from subprocess import run

camera = cv2.VideoCapture(0)
_, frame = camera.read()
camera.set(44, 0)

print(f'Frame dimensions: {frame.shape[:2]}')
mask = np.zeros(frame.shape[:2], np.uint8)
# mask[200:280, 0:120] = 255 # Comment this to get full frame
mask[:, :] = 255 # Comment this to get full frame

hues = [100]
hue_margin = 10

class ColorDetector:

    COLORS = {
        'red': 4,
        'green': 60,
        'blue': 117
    }
    HUE_MARGIN = 10
    HUE_THRESHOLD = 600
    CAMERA_CTRLS = {
        'auto_exposure': 1,
        # TODO
    }
    IMG_SIZE = (640, 480)
    CIRCLE_RADIUS = 50
    CIRCLE_ARRAY_SIZE = (5, 4)
    CIRCLE_ARRAY_PITCH = (114, 112)
    CIRCLE_ARRAY_POSITION = (108, -75)
    CIRCLE_ARRAY_ROTATION = 1.5

    def __init__(self):
        self.circles_mask = self._create_circles_mask()
        n = self.CIRCLE_ARRAY_SIZE[0] * self.CIRCLE_ARRAY_SIZE[1]
        self.result = [None for _ in range(n)]

    def load_img(self, img):
        self.img = img
        self.img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        self.filter_mask = self._create_filter_mask()

    def detect_colors(self):
        res = [self._detect_circle_color(roi) for roi in self._iter_circles()]
        self.result = res
        return res

    def _detect_circle_color(self, roi):

        m, th = self.HUE_MARGIN, self.HUE_THRESHOLD
        hist = self._compute_hist(img=self.img_hsv[roi],
                                  mask=self.filter_mask[roi])

        for name, hue in self.COLORS.items():
            if self._sum_in_range(hist, hue - m, hue + m) > th:
                return name

        return None

    def plot_hist(self):

        hist = self._compute_hist(img=self.img_hsv,
                                  mask=self.filter_mask)
        lines = plt.plot(hist, color='black')

        for hue in self.COLORS.values():
            xmin = (hue - self.HUE_MARGIN) % 180
            xmax = (hue + self.HUE_MARGIN) % 180
            color = np.array(self._hue_to_rgb(hue)) / 255
            lines += [plt.axvline(x=xmin, color=color, linestyle='--')]
            lines += [plt.axvline(x=xmax, color=color, linestyle='--')]

        return lines

    def show(self, filter_mask=False):
        if filter_mask:
            cv2.imshow('Frame', cv2.bitwise_and(self.img,
                                                self.img,
                                                mask=self.filter_mask))
        else:
            cv2.imshow('Frame', self.img)

    def draw_circles(self, thickness=1):

        for pos, res in zip(self._iter_circles_positions(), self.result):

            if res is None:
                color = [255, 255, 255]
            else:
                hue = self.COLORS[res]
                color = self._hue_to_bgr(hue)

            cv2.circle(img=self.img,
                       center=tuple(pos),
                       radius=self.CIRCLE_RADIUS,
                       color=color,
                       thickness=thickness)

    def _compute_hist(self, img, mask):
        return cv2.calcHist(images=[img],
                            channels=[0],
                            mask=mask,
                            histSize=[180],
                            ranges=[0, 180])

    def _create_filter_mask(self):

        mask_sat = cv2.inRange(self.img_hsv[:, :, 1], 100, 255)
        mask = cv2.bitwise_and(self.circles_mask, mask_sat)

        mask_val = cv2.inRange(self.img_hsv[:, :, 2], 90, 255)
        mask = cv2.bitwise_and(mask, mask_val)

        return mask

    def _create_circles_mask(self):

        mask = np.zeros(shape=self.IMG_SIZE[::-1], dtype='uint8')

        for pos in self._iter_circles_positions():

            cv2.circle(img=mask,
                       center=tuple(pos),
                       radius=self.CIRCLE_RADIUS,
                       color=1,
                       thickness=cv2.FILLED)

        return mask

    def _iter_circles(self):
        r = self.CIRCLE_RADIUS
        for x, y in self._iter_circles_positions():
            yield slice(y - r, y + r), slice(x - r, x + r)

    def _iter_circles_positions(self):

        nx, ny = self.CIRCLE_ARRAY_SIZE
        dx, dy = self.CIRCLE_ARRAY_PITCH
        px, py = self.CIRCLE_ARRAY_POSITION
        positions_x = np.linspace(-1, 1, nx) * (nx - 1) / 2 * dx + px
        positions_y = np.linspace(-1, 1, ny) * (ny - 1) / 2 * dy + py

        rot = np.radians(self.CIRCLE_ARRAY_ROTATION)
        rot = np.array([[np.cos(rot), np.sin(rot)],
                        [-np.sin(rot), np.cos(rot)]])

        center = self.IMG_SIZE[1] / 2, self.IMG_SIZE[0] / 2

        for x in positions_x:
            for y in positions_y:
                pos = rot.dot([x, y]) + center
                yield np.round(pos).astype(int)

    def _sum_in_range(self, y, xmin, xmax, x=None):
        y = np.array(y)
        if x is None:
            x = np.array(range(len(y)))
        mask = np.logical_and(xmin <= x, x <= xmax)
        return np.sum(y[mask])

    def _hue_to_bgr(self, hue):
        hsv = np.array([[[hue, 255, 255]]], dtype='uint8')
        color = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)[0, 0]
        return [int(i) for i in color]

    def _hue_to_rgb(self, hue):
        hsv = np.array([[[hue, 255, 255]]], dtype='uint8')
        color = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)[0, 0]
        return [int(i) for i in color]


def animate(i, color_detector):
    if camera.isOpened():

        # read camera and get hsv
        # ret, frame = camera.read()
        img = cv2.imread('./potion_maker_test.png')
        color_detector.load_img(img)
        color_detector.draw_circles()
        color_detector.show(filter_mask=False)

        color_detector.detect_colors()
        lines = color_detector.plot_hist()

        # cv2.imshow('Frame', cv2.bitwise_and(frame, frame, mask=mask))

        # cv2.imshow('Frame', circles)
        # cv2.imshow('Frame', frame)
        # cv2.imshow('Frame', cv2.bitwise_and(frame, frame, mask=mask))
        # cv2.imshow('Frame', circles)

    return lines


color_detector = ColorDetector()
figure, axis = plt.subplots()
ma = animation.FuncAnimation(figure,
                             lambda i: animate(i, color_detector),
                             interval=10,
                             blit=True,
                             repeat=True)
plt.show()

camera.release()
cv2.destroyAllWindows()
