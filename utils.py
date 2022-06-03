import pygame
import time
import datetime as dt
import random
import sys
import os
from PIL import Image, ImageOps
import logging
from typing import Tuple


class ImageEditor:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def scale(
            self, output_image_path: str,
            width: int = None,
            height: int = None
    ):
        original_image = Image.open(self.file_path)
        w, h = original_image.size
        logging.debug(f'Original image size is {w}x{h}')
        if width and height:
            max_size = (width, height)
        elif width:
            max_size = (width, h)
        elif height:
            max_size = (w, height)
        else:
            raise RuntimeError('Width or height required!')
        original_image.thumbnail(max_size, Image.ANTIALIAS)
        original_image.save(output_image_path)
        scaled_image = Image.open(output_image_path)
        width, height = scaled_image.size
        logging.debug(f'Scaled image size is {width}x{height}')

    def mirror(self):
        im = Image.open(self.file_path)
        im_mirror = ImageOps.mirror(im)
        im_mirror.save(self.file_path, quality=95)

    def flip(self):
        im = Image.open(self.file_path)
        im_flip = ImageOps.flip(im)
        im_flip.save(self.file_path, quality=95)


def random_rgb(theme: str = 'dark', dominate: str = None) -> Tuple[int, int, int]:
    top = 100 if theme == 'dark' else 255
    bottom = 0 if theme == 'dark' else 200
    r, g, b = random.randint(bottom, top), random.randint(bottom, top), random.randint(bottom, top)
    if dominate == 'red':
        r = 255
    elif dominate == 'green':
        g = 255
    return r, g, b
