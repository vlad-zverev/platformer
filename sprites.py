from abc import ABC
from typing import List

import random
import pygame
from image import ImageEditor


class BaseSprite(ABC, pygame.sprite.Sprite, ImageEditor):
    def __init__(
            self, file: str,
            can_move: bool = True,
            stamina: int = 100,
            health_points: int = 100
    ):
        pygame.sprite.Sprite.__init__(self)
        ImageEditor.__init__(self, file, 50)
        self.rect = self.image.get_rect()
        self.can_move = can_move
        self.stamina = stamina
        self.health_points = health_points

    def update(self, destination: List[str], dist: int = 10):
        self.move(destination, dist)

    def move(self, destination, move_dist: int = 5):
        diagonal_dist = move_dist / (2 ** 0.5)
        destination = set(destination)
        if self.can_move and destination != {'stop'}:
            if destination == {'right'}:
                self.rect.x += move_dist
            elif destination == {'left'}:
                self.rect.x -= move_dist
            elif destination == {'up'}:
                self.rect.y -= move_dist
            elif destination == {'down'}:
                self.rect.y += move_dist
            elif sorted(destination) == sorted({'down', 'left'}):
                self.rect.x -= diagonal_dist
                self.rect.y += diagonal_dist
            elif sorted(destination) == sorted({'up', 'right'}):
                self.rect.x += diagonal_dist
                self.rect.y -= diagonal_dist
            elif sorted(destination) == sorted({'down', 'right'}):
                self.rect.x += diagonal_dist
                self.rect.y += diagonal_dist
            elif sorted(destination) == sorted({'left', 'up'}):
                self.rect.x -= diagonal_dist
                self.rect.y -= diagonal_dist
            else:
                raise ValueError(f'Invalid destination: {destination}')

    def hit_box(self):
        hit_box = self.rect.copy()
        hit_box.height /= 2.5
        hit_box.width /= 2.5
        hit_box.center = self.rect.center
        return hit_box


class Food(BaseSprite):
    def __init__(self, health_benefits: int, file: str, utility: int):
        super().__init__(file)
        self.health_benefits = health_benefits if health_benefits else 1
        self.utility = utility if utility else 1


class Gun(BaseSprite):
    def __init__(self, file: str):
        super().__init__(file)

    def fire(self):
        return pygame.Rect(
            10,
            10,
            10,
            10,
        )


class Enemy(BaseSprite):
    def __init__(self, file: str, speed: int, health_points: int = 150):
        super().__init__(file, health_points=health_points)
        self.speed = speed


class Player(BaseSprite):
    def __init__(self, file: str, gun: Gun):
        super().__init__(file)
        self.gun = gun

    def update(self, destination: List[str], dist: int = 10):
        self.move(destination, dist)
        self.fire()

    def consume(self, food: Food):
        self.health_points += food.health_benefits
        self.stamina += food.utility

    def fire(self):
        return self.gun.fire()
