import pygame
from pygame.sprite import Sprite

class Alien(Sprite):
    '''Класс представляющий одного пришельца'''
    def __init__(self, ai_game):
        '''Инициализирует пришельца и задает его начальную позицию'''
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings

        # Загрузка изображения и назначение атрибута rect
        self.image = pygame.image.load('images/alien2.bmp')
        self.rect = self.image.get_rect()

        # Каждый новый пришелец появляется в левом углу экрана
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height

        # Сохранение горизонтальной позиции пришельца
        self.x = float(self.rect.x)

    def update(self):
        '''Перемещение пришельца вправо или влево'''
        self.x += (self.settings.alien_speed * self.settings.fleet_direction)
        self.rect.x = self.x

    def check_edges(self):
        '''Возвращает True если пришелец у края экрана'''
        screen_rect = self.screen.get_rect()
        if self.rect.right >= screen_rect.right or self.rect.left <= 0:
            return True
