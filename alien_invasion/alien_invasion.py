import sys
import pygame
from time import sleep
from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from game_stats import GameStats
from button import Button
from scoreboard import ScoreBoard
import random

save_path = 'save/high_score.txt'


class AlienInvasion:
    """Класс для управления ресурсами и поведением игры"""

    def __init__(self):
        """Инициализирует игру и создает ресурсы"""
        pygame.init()
        self.settings = Settings()
        # Запуск в окне
        # self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        # Запуск в полноэкранном режиме
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption('Alien Invasion')
        self.sound1 = pygame.mixer.Sound('music/bullet.mp3')
        self.sound2 = pygame.mixer.Sound('music/exp.mp3')
        self.sound3 = pygame.mixer.Sound('music/dead.mp3')
        self.sound2.set_volume(0.2)
        self.sound1.set_volume(0.8)
        # Музыка
        pygame.mixer.music.load('music/intro.ogg')
        pygame.mixer.music.play(10)
        # Статистика
        # Игровая статистика
        self.stats = GameStats(self)
        self.sb = ScoreBoard(self)
        logo = pygame.image.load('images/icon.png')
        # Фон по уровням
        self.background = pygame.image.load('images/bg.jpg')
        self.background2 = pygame.image.load('images/bg2.jpg')
        self.background3 = pygame.image.load('images/bg3.jpg')
        self.background4 = pygame.image.load('images/bg4.jpg')
        pygame.display.set_icon(logo)
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self._create_fleet()
        # Создание кнопки
        self.play_button = Button(self, "Play")

    def run_game(self):
        """Запуск игрового цыкла игры"""
        while True:
            self._check_events()
            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
            self._update_screen()

    def _check_events(self):
        """Обрабатывает нажатия клавиш"""
        for event in pygame.event.get():
            # Обрабатываем событие при закрытии окна
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)

    def _save_score(self):
        """Сохранение рекорда"""
        with open(save_path, 'w') as file:
            file.write(str(self.stats.high_score))

    def _load_score(self):
        """Загрузка рекорда"""
        try:
            if save_path:
                with open(save_path, 'r') as f:
                    self.stats.high_score = int(f.read())
                self.sb.prep_high_score()
        except FileNotFoundError:
            print('Файла сохранения не существует, создаю....')
            with open(save_path, 'w') as f:
                f.write(str(self.stats.high_score))

    def _check_play_button(self, mouse_pos):
        """Запускает новую игру при нажатии на play"""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            pygame.mixer.music.load('music/level_9_12.mp3')
            pygame.mixer.music.queue('music/level1_3.mp3')
            pygame.mixer.music.queue('music/level4_8.ogg')
            pygame.mixer.music.play()
            self.settings.initialize_dynamic_settings()
            self.stats.reset_stats()
            self._load_score()
            self.stats.game_active = True
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()
            # Очстка пришельцев и снарядов
            self.aliens.empty()
            self.bullets.empty()
            # Создание новго флота
            self._create_fleet()
            self.ship.center_ship()
            pygame.mouse.set_visible(False)

    def _check_keydown_events(self, event):
        # Обрабатываем нажатие на кнопку
        if event.key == pygame.K_RIGHT:
            # Переместить корабль вправо
            self.ship.moving_right = True
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
        elif event.key == pygame.K_LEFT:
            # Переместить корабль влево
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            self._save_score()
            sys.exit()

    def _check_keyup_events(self, event):
        # Кнопка отпущена
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _ship_hit(self):
        self.sound3.play()
        '''Столкновение корабля с пришельцем'''
        if self.stats.ships_left > 0:
            self.stats.ships_left -= 1
            self.sb.prep_ships()
            # Очистка снарядов и пришельцев
            self.aliens.empty()
            self.bullets.empty()
            # Создание новго флота
            self._create_fleet()
            self.ship.center_ship()
            # Пауза
            sleep(0.5)
        else:
            pygame.mixer.music.load('music/game_over.ogg')
            pygame.mixer.music.play(10)
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def _create_alien(self, alien_number, row_number):
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)

    def _check_fleet_edges(self):
        """Реагирует на достижение пришельцем края экрана"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """Опускает флот, и меняет направление"""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _create_fleet(self):
        """Создание флота"""
        # Интервал между пришельцами равен ширине пришельца
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)
        '''Определяет кол-во рядов на экране'''
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)

        # Создание первого ряда пришельцев
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)

    def _fire_bullet(self):
        if self.stats.game_active:
            '''Создание снаряда и добавление в группу Bullets'''
            if len(self.bullets) < self.settings.bullets_allowed:
                new_bullet = Bullet(self)
                self.bullets.add(new_bullet)
                self.sound1.play()

    def _update_bullets(self):
        self.bullets.update()
        # Удаление снарядов
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        self._check_bullet_alien_collisions()

    def _star_new_level(self):
        """Начало нового вровня"""
        self.bullets.empty()
        self._create_fleet()
        self.settings.increase_speed()
        # Увеличение уровня
        self.stats.level += 1
        self.sb.prep_level()

    def _check_bullet_alien_collisions(self):
        # Проверка попадания
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        if collisions:
            self.sound2.play()
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)

            self.sb.prep_score()
            self.sb.check_high_score()
        # Проверка остались ли пришельцы
        if not self.aliens:
            self._star_new_level()

    def _check_aliens_bottom(self):
        """Проверяет добрались ли пришельцы до нижнего края экрана"""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                self._ship_hit()
                break

    def _update_aliens(self):
        """Обновляет позиции всех пришельцев во флоте"""
        self._check_fleet_edges()
        self.aliens.update()
        # Проверка коллизии пришелец-корабль
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
        # Проверить добрались ли пришельцы до нижнего края экрана
        self._check_aliens_bottom()

    def _update_screen(self):
        # При каждом проходе цыкла прорисовывать экран
        self.screen.fill(self.settings.bg_color)
        if self.stats.level < 3:
            self.screen.blit(self.background, (0, 0))
        elif self.stats.level < 8:
            self.screen.blit(self.background2, (0, 0))
        elif self.stats.level < 12:
            self.screen.blit(self.background3, (0, 0))
        else:
            self.screen.blit(self.background4, (0, 0))
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)
        self.sb.show_score()
        if not self.stats.game_active:
            self.play_button.draw_button()
        # Отображение экрана
        pygame.display.flip()


if __name__ == '__main__':
    # создание экземпляра и запуск игры
    ai = AlienInvasion()
    ai.run_game()
