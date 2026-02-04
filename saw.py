import pygame

class Saw(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # Load saw images
        try:
            self.chain_img = pygame.image.load("assets/Traps/Saw/Chain.png").convert_alpha()
            self.off_img = pygame.image.load("assets/Traps/Saw/off.png").convert_alpha()
            self.on_img = pygame.image.load("assets/Traps/Saw/on.png").convert_alpha()
            
            # Scale images to appropriate size
            self.chain_img = pygame.transform.scale(self.chain_img, (64, 64))
            self.off_img = pygame.transform.scale(self.off_img, (64, 64))
            self.on_img = pygame.transform.scale(self.on_img, (64, 64))
            
            # Set initial image
            self.image = self.off_img
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.mask = pygame.mask.from_surface(self.image)
            
            # Animation properties
            self.animation_speed = 0.1
            self.animation_counter = 0
            self.is_active = False
            self.activation_timer = 0
            self.activation_delay = 60  # Frames between activations
            
        except pygame.error as e:
            print(f"⚠️ Error loading Saw images: {e}")
            # Create a fallback red circle if images fail to load
            self.image = pygame.Surface((64, 64))
            self.image.fill((255, 0, 0))
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.mask = pygame.mask.from_surface(self.image)
            self.is_active = False
    
    def update(self, shift=0):
        """Update saw animation and state"""
        self.animation_counter += self.animation_speed
        
        # Toggle active state based on timer
        self.activation_timer += 1
        if self.activation_timer >= self.activation_delay:
            self.is_active = not self.is_active
            self.activation_timer = 0
        
        # Update image based on state
        if self.is_active:
            self.image = self.on_img
        else:
            self.image = self.off_img
        
        # Update mask for collision detection
        self.mask = pygame.mask.from_surface(self.image)
        
        # Apply shift if provided
        self.rect.x += shift
    
    def draw(self, window, offset_x):
        """Draw the saw with chain"""
        # Draw chain above the saw
        chain_x = self.rect.x - offset_x
        chain_y = self.rect.y - 32  # Chain above the saw
        
        # Draw chain
        window.blit(self.chain_img, (chain_x, chain_y))
        
        # Draw saw
        saw_x = self.rect.x - offset_x
        saw_y = self.rect.y
        window.blit(self.image, (saw_x, saw_y))
    
    def collide(self, player):
        """Check collision with player"""
        return self.rect.colliderect(player.rect)
    
    def get_damage(self):
        """Return damage when player touches active saw"""
        return 1 if self.is_active else 0
