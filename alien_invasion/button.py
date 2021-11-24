import pygame.font

class Button:
    def __init__(self, ai_game, msg):
        '''Инициализирует атрибуты кнопки'''
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()
        # Назначение размеров и свойства кнопок
        self.width, self.height = 200, 94
        #self.button_color = (246, 210, 60)
        #self.text_color = (0, 0, 0)
        self.btn_image = pygame.image.load('images/btn2.png')
        #self.font = pygame.font.SysFont(None, 48)
        # Построение объекта rect кнопки
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = self.screen_rect.center
        self.rect.y = 600
        # Сообщение кнопки создается 1 раз
        self._prep_msg(msg)

    def _prep_msg(self, msg):
        '''Преобразует msg и выравнивает по центру'''
        #self.msg_image = self.font.render(msg, True, self.text_color, self.button_color)
        self.msg_image_rect = self.btn_image.get_rect()
        self.msg_image_rect.center = self.rect.center

    def draw_button(self):
        # Отображение пустой кнопки и вывод сообщения
        #self.screen.fill(self.button_color, self.rect)
        self.screen.blit(self.btn_image, self.msg_image_rect)
