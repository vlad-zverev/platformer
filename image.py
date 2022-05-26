import logging
import pygame

from PIL import Image, ImageOps


class ImageEditor:
	def __init__(self, file_path: str, width: int = None, height: int = None):
		self.file_path = f'img/{file_path}.png'
		self.scale(f'img/{file_path}_scaled.png', width, height)
		self.image = pygame.image.load(self.file_path).convert_alpha()

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
		self.file_path = output_image_path

	def mirror(self):
		im = Image.open(self.file_path)
		im_mirror = ImageOps.mirror(im)
		im_mirror.save(self.file_path, quality=95)

	def flip(self):
		im = Image.open(self.file_path)
		im_flip = ImageOps.flip(im)
		im_flip.save(self.file_path, quality=95)
