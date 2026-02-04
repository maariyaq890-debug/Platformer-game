import pygame

class FallingPlatform(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.images = {
            "on": pygame.image.load("assets/Traps/FallingPlatforms/On.png").convert_alpha(),
            "off": pygame.image.load("assets/Traps/FallingPlatforms/Off.png").convert_alpha()
        }
        self.image = self.images["on"]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.falling = False
        self.fall_speed = 0
        self.timer = 0
        self.triggered = False

    def update(self, player):
        if self.rect.colliderect(player.rect) and not self.triggered:
            self.triggered = True
            self.timer = 30  # Delay before it starts falling

        if self.triggered:
            self.timer -= 1
            if self.timer <= 0:
                self.falling = True

        if self.falling:
            self.fall_speed += 0.5  # gravity
            self.rect.y += self.fall_speed
            self.image = self.images["off"]

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))
    def collide(self, player):
        if self.rect.colliderect(player.rect):
        # Is player landing on platform from above?
            if player.y_vel > 0 and player.rect.bottom - self.rect.top < 15:
            # ✅ Trigger fall
                if not self.falling:
                    self.falling = True
                    self.fall_timer = 20  # Delay frames before falling

            # ✅ Make player stand on platform
                player.rect.bottom = self.rect.top
                player.y_vel = 0
                player.jump_count = 0

    
