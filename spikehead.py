import pygame

class SpikeHead(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # Load all SpikeHead images
        self.images = {
            "idle": pygame.image.load("assets/Traps/SpikeHead/idle.png").convert_alpha(),
            "blink": pygame.image.load("assets/Traps/SpikeHead/Blink.png").convert_alpha(),
            "left": pygame.image.load("assets/Traps/SpikeHead/LeftHit.png").convert_alpha(),
            "right": pygame.image.load("assets/Traps/SpikeHead/RightHit.png").convert_alpha(),
            "top": pygame.image.load("assets/Traps/SpikeHead/TopHit.png").convert_alpha(),
            "bottom": pygame.image.load("assets/Traps/SpikeHead/BottomHit.png").convert_alpha(),
        }

        self.state = "idle"
        self.image = self.images[self.state]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        self.name = "spikehead"
        self.timer = 0
        self.animation_time = 20  # frames to show animation

    def update(self, player):
        # Add blinking animation when idle
        if self.state == "idle" and self.timer == 0:
            # Randomly blink every few seconds
            if pygame.time.get_ticks() % 3000 < 500:  # Blink for 500ms every 3 seconds
                self.state = "blink"
        
        if self.rect.colliderect(player.rect):
            # Detect direction of collision
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery

            if abs(dx) > abs(dy):
                self.state = "right" if dx > 0 else "left"
            else:
                self.state = "bottom" if dy > 0 else "top"

            self.timer = self.animation_time
        elif self.timer > 0:
            self.timer -= 1
            if self.timer == 0:
                self.state = "idle"
        elif self.state == "blink":
            # Return to idle after blink
            self.state = "idle"

        self.image = self.images[self.state]
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))
        
    def collide(self, player):
        """Check collision with player"""
        return self.rect.colliderect(player.rect)
    
    def get_damage(self):
        """Return damage when player touches SpikeHead"""
        return 1
