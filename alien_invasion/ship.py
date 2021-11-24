import pygame
from pygame.sprite import Sprite

class Ship(Sprite):
    '''Класс для управления кораблем'''

    def __init__(self, ai_game):
        super().__init__()
        """Инициализирует корабль и задает его начальную позицию."""
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.screen_rect = ai_game.screen.get_rect()
        # Загружает изображение корабля и получает прямоугольник.
        self.image = pygame.image.load('images/ship.bmp')
        self.rect = self.image.get_rect()
        # Каждый новый корабль появляется у нижнего края экрана.
        self.rect.midbottom = self.screen_rect.midbottom
        # Сохранение вещественной координаты корабля
        self.x = float(self.rect.x)
        # Флаг перемещения
        self.moving_right = False
        self.moving_left = False

    def update(self):
        '''Обновляет позицию корабля с учетом флага'''
        # sels.rect.right возвращает координату x правого края корабля
        # Чтобы корабль не выходил за пределы экрана
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.settings.ship_speed
        if self.moving_left and self.rect.left > 0:
            self.x -= self.settings.ship_speed
        # Обновление атрибута rect на основании x
        self.rect.x = self.x

    def blitme(self):
            self.screen.blit(self.image, self.rect)

    def center_ship(self):
        '''Размещает корабль в центре'''
        self.rect.midbottom = self.screen_rect.midbottom
        self.x = float(self.rect.x)