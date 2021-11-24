class Settings:
    """Настройки Alien Invasion."""

    def __init__(self):
        """Инициализация настроек"""
        # Screen settings
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (230, 230, 230)

        # Ship settings
        self.ship_limit = 1

        # Bullet settings
        self.bullet_width = 13
        self.bullet_height = 30
        self.bullets_allowed = 3

        # Alien settings
        self.fleet_drop_speed = 10

        # Темп ускорения игры
        self.speedup_scale = 1.1
        # Темп роста очков
        self.score_scale = 1.5

        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        """Доп.настройки скорости игры."""
        self.ship_speed = 2
        self.bullet_speed = 4.0
        self.alien_speed = 1

        # fleet_direction of 1 represents right; -1 represents left.
        self.fleet_direction = 1
        # Подсчет очков
        self.alien_points = 50

    def increase_speed(self):
        """Increase speed settings."""
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale

        self.alien_points = int(self.alien_points * self.score_scale)