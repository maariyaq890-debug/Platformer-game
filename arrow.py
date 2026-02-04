import pygame
import os

class Arrow(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.frames = []
        self.load_images()
        self.current_frame = 0
        self.animation_speed = 0.2
        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        self.animating = False

    def load_images(self):
        path = "assets/Traps/Arrow/"
        self.frames.append(pygame.image.load(os.path.join(path, "idle.png")).convert_alpha())
        self.frames.append(pygame.image.load(os.path.join(path, "hit.png")).convert_alpha())

    def trigger_animation(self):
        self.animating = True
        self.current_frame = 0

    def update(self, shift=0):
        self.rect.x += shift
        if self.animating:
            self.current_frame += self.animation_speed
            if self.current_frame >= len(self.frames):
                self.current_frame = 0
                self.animating = False
            self.image = self.frames[int(self.current_frame)]

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))

    def collide(self, player):
        if self.rect.colliderect(player.rect):
            self.trigger_animation()
            return True
        return False
