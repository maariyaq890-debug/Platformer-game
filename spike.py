import pygame

class Spike(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("assets/Traps/Spikes/Idle.png").convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, shift=0):
        self.rect.x += shift

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))    
    
    def collide(self, player):
        return self.rect.colliderect(player.rect)
