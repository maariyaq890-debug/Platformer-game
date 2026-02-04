import pygame

class RockHead(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # Load rock head images
        try:
            # Use SpikeHead images since Rock_Head has the same images
            self.idle_img = pygame.image.load("assets/Traps/SpikeHead/Idle.png").convert_alpha()
            self.attack_img = pygame.image.load("assets/Traps/SpikeHead/Idle.png").convert_alpha()
            
            # Scale images to appropriate size
            self.idle_img = pygame.transform.scale(self.idle_img, (64, 64))
            self.attack_img = pygame.transform.scale(self.attack_img, (64, 64))
            
            # Set initial image
            self.image = self.idle_img
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.mask = pygame.mask.from_surface(self.image)
            
            # Animation properties
            self.animation_speed = 0.1
            self.animation_counter = 0
            self.is_attacking = False
            self.attack_timer = 0
            self.attack_delay = 120  # Frames between attacks
            self.attack_duration = 30  # How long attack lasts
            
        except pygame.error as e:
            print(f"⚠️ Error loading RockHead images: {e}")
            # Create a fallback brown circle if images fail to load
            self.image = pygame.Surface((64, 64))
            self.image.fill((139, 69, 19))  # Brown color
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.mask = pygame.mask.from_surface(self.image)
            self.is_attacking = False
    
    def update(self, shift=0):
        """Update rock head animation and state"""
        self.animation_counter += self.animation_speed
        
        # Handle attack timing
        if not self.is_attacking:
            self.attack_timer += 1
            if self.attack_timer >= self.attack_delay:
                self.is_attacking = True
                self.attack_timer = 0
        else:
            self.attack_timer += 1
            if self.attack_timer >= self.attack_duration:
                self.is_attacking = False
                self.attack_timer = 0
        
        # Update image based on state
        if self.is_attacking:
            self.image = self.attack_img
        else:
            self.image = self.idle_img
        
        # Update mask for collision detection
        self.mask = pygame.mask.from_surface(self.image)
        
        # Apply shift if provided
        self.rect.x += shift
    
    def draw(self, window, offset_x):
        """Draw the rock head"""
        x = self.rect.x - offset_x
        y = self.rect.y
        window.blit(self.image, (x, y))
    
    def collide(self, player):
        """Check collision with player"""
        return self.rect.colliderect(player.rect)
    
    def get_damage(self):
        """Return damage when player touches attacking rock head"""
        return 1 if self.is_attacking else 0
