import random
import sys
from datetime import datetime
from typing import Tuple

import pygame

from sprites import Player, Enemy, Gun
from utils import random_rgb
from typing import List


class Star:
    def __init__(self, stars: list, screen_weight: int, screen_height: int):
        self.size = random.randint(2, 4)
        self.rect = pygame.Rect(
            screen_weight - 1,
            random.randint(1, screen_height),
            self.size,
            self.size,
        )
        self.speed = random.randint(-20, -2)
        stars.append(self)


class EventHandler:
    def __init__(self, event: pygame.event.Event, state: List[str], fire: bool):
        self.state = state
        self.fire = fire
        self.mouse(event)
        self.buttons(event)
        if not self.state:
            self.state = ['stop']

    def mouse(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.start_moving()
            if 'down' not in self.state:
                self.state.append('up')
        if event.type == pygame.MOUSEBUTTONUP:
            if 'up' in self.state:
                self.state.remove('up')

    def buttons(self, event):
        if event.type == pygame.KEYDOWN:
            self.start_moving()
            if event.key == pygame.K_DOWN:
                if 'up' not in self.state:
                    self.state.append('down')
            if event.key == pygame.K_UP:
                if 'down' not in self.state:
                    self.state.append('up')
            if event.key == pygame.K_LEFT:
                if 'right' not in self.state:
                    self.state.append('left')
            if event.key == pygame.K_RIGHT:
                if 'left' not in self.state:
                    self.state.append('right')
            if event.key == pygame.K_SPACE:
                self.fire = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                if 'down' in self.state:
                    self.state.remove('down')
            if event.key == pygame.K_UP:
                if 'up' in self.state:
                    self.state.remove('up')
            if event.key == pygame.K_LEFT:
                if 'left' in self.state:
                    self.state.remove('left')
            if event.key == pygame.K_RIGHT:
                if 'right' in self.state:
                    self.state.remove('right')
            if event.key == pygame.K_SPACE:
                self.fire = False

    def start_moving(self):
        try:
            self.state.remove('stop')
        except ValueError:
            pass


class Game:
    iter = 0
    FPS = 100
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    bg_size = (1080, 720)
    running = True
    fire = False
    finished_at = None

    def __init__(self, name: str = 'Platformer'):
        self.name = name
        self.background = pygame.Surface(self.bg_size)
        self.weight, self.height = self.bg_size
        self.screen = pygame.display.set_mode(self.bg_size)
        self.clock = pygame.time.Clock()

        self.fire_track = None
        self.state = ['stop']
        self.started_at = datetime.now()
        self.cooldown = 100
        self.enemies_killed = 0
        self.enemies_missed = 0

        self.gun = Gun(file='bluster')
        self.player = Player(file='player', gun=self.gun)
        self.enemies_sprites = pygame.sprite.Group()
        self.stars: List[Star] = []

    def run(self):
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption(self.name)
        while self.running:
            self.loop()
        sys.exit()

    def loop(self):
        self.clock.tick(self.FPS)
        self.screen.blit(self.background, (0, 0))
        for event in pygame.event.get():
            self.handle_event(event)
            if event.type == pygame.QUIT:
                self.running = False
        self.draw()
        pygame.display.update()

    def handle_event(self, event: pygame.event.Event):
        event_handler = EventHandler(event=event, state=self.state, fire=self.fire)
        self.state = event_handler.state
        self.fire = event_handler.fire

    def draw(self):
        self.screen.fill(self.BLACK)
        self.draw_stars()
        self.update_player()
        self.update_enemies()
        self.set_permanent_texts()

    def set_text(
            self, text: str,
            font_type: str = 'Arial',
            color: Tuple[int, int, int] = None,
            size: int = 36,
            position: Tuple[int, int] = (100, 100)
    ):
        font = pygame.font.SysFont(font_type, size, bold=pygame.font.Font.bold)
        text = font.render(text, True, color if color else random_rgb())
        self.screen.blit(text, position)

    def health_banner(self):
        self.set_text(
            f'health {self.player.health_points}/100',
            color=random_rgb(theme='bright') if self.player.health_points > 30 else (255, 100, 100),
            position=(self.weight - 180, 10),
            size=18
        )

    def set_permanent_texts(self):
        self.health_banner()
        self.cooldown_weapon_banner()
        self.counters_text()

    def counters_text(self):
        self.set_text(
            f'killed {self.enemies_killed}',
            color=random_rgb(theme='bright'),
            position=(300, 10),
            size=18
        )
        self.set_text(
            f'missed {self.enemies_missed}',
            color=random_rgb(theme='bright'),
            position=(300, 40),
            size=18
        )

    def cooldown_weapon_banner(self):
        pygame.draw.rect(self.screen, random_rgb(), pygame.Rect(20, 10, 125, 25))
        pygame.draw.rect(self.screen, random_rgb(dominate='red'), pygame.Rect(22, 12, 120 * (self.cooldown / 100), 20))

    def draw_stars(self):
        Star(self.stars, self.weight, self.height)
        for star in self.stars:
            star.rect = star.rect.move(star.speed, 0)
            pygame.draw.rect(self.screen, self.WHITE, star.rect)
            if star.rect.right < 0:
                self.stars.remove(star)

    def spawn_enemies(self):
        if len(self.enemies_sprites) < 3:
            enemy = Enemy(file='monster', speed=random.randint(1, 4))
            enemy.rect.x, enemy.rect.y = self.weight - 50, int(self.height / (random.randint(15, 50) / 10))
            self.enemies_sprites.add(enemy)

    def check_player_death(self):
        if self.player.health_points <= 0:
            if self.player.can_move:
                self.finished_at = datetime.now()
            self.death_banner()
            self.player.health_points = 0
            self.player.kill()
            self.player.can_move = False

    @staticmethod
    def hit_handler(player, hit_box):
        if hit_box:
            if hit_box.colliderect(player.rect):
                player.health_points -= random.randint(5, 10)

    @staticmethod
    def check_sprite_out_of_screen(sprite):
        if sprite.rect.x < -sprite.rect.width:
            sprite.kill()
            del sprite

    def death_banner(self):
        self.set_text(
            f'DEAD',
            color=random_rgb(dominate='red'),
            position=(400, 200),
            size=80
        )
        self.set_text(
            f'session time {str(self.finished_at - self.started_at)[:-7]}',
            color=self.WHITE,
            position=(350, 400),
            size=30
        )

    def update_player(self):
        self.check_player_death()
        if self.cooldown < 100:
            self.cooldown += 0.5
        self.player.update(destination=self.state, dist=5)
        self.screen.blit(self.player.image, (self.player.rect.x, self.player.rect.y))
        self.screen.blit(self.gun.image, (self.player.rect.x + 35, self.player.rect.y + 30))
        if self.fire and self.cooldown > 0:
            self.cooldown -= 1
            self.fire_track = pygame.Rect(self.player.rect.x + 80, self.player.rect.y + 35, 800, 5)
            pygame.draw.rect(self.screen, random_rgb(dominate='red'), self.fire_track)

    def update_enemies(self):
        self.spawn_enemies()
        for enemy in self.enemies_sprites:
            enemy.rect = enemy.rect.move(-enemy.speed, 0)
            self.hit_handler(enemy, self.fire_track)
            self.hit_handler(self.player, enemy.hit_box())
            self.screen.blit(enemy.image, (enemy.rect.x, enemy.rect.y))
            if enemy.rect.right < 0:
                self.enemies_missed += 1
                enemy.kill()
                del enemy
            elif enemy.health_points <= 0:
                self.enemies_killed += 1
                enemy.kill()
                del enemy


Game().run()
