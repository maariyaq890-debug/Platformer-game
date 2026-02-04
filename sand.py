import pygame

class Sand(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # Load sand images
        try:
            # Try to load sand particle images
            print("🟡 Loading Sand trap images...")
            self.sand_img = pygame.image.load("assets/Traps/Sand/Sand Particle.png").convert_alpha()
            self.mud_img = pygame.image.load("assets/Traps/Sand/Mud Particle.png").convert_alpha()
            print("✅ Sand trap images loaded successfully")
            
            # Scale images to appropriate size
            self.sand_img = pygame.transform.scale(self.sand_img, (64, 64))
            self.mud_img = pygame.transform.scale(self.mud_img, (64, 64))
            
            # Set initial image
            self.image = self.sand_img
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.mask = pygame.mask.from_surface(self.image)
            
            # Animation properties
            self.animation_speed = 0.1
            self.animation_counter = 0
            self.is_active = True  # Sand is always active
            self.state_timer = 0
            self.state_delay = 60  # Frames between state changes
            
        except pygame.error as e:
            print(f"⚠️ Error loading Sand images: {e}")
            # Create a fallback yellow rectangle if images fail to load
            self.image = pygame.Surface((64, 64))
            self.image.fill((255, 255, 0))
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.mask = pygame.mask.from_surface(self.image)
            self.is_active = True
    
    def update(self, shift=0):
        """Update sand animation and state"""
        self.animation_counter += self.animation_speed
        
        # Toggle between sand and mud states
        self.state_timer += 1
        if self.state_timer >= self.state_delay:
            self.is_active = not self.is_active
            self.state_timer = 0
        
        # Update image based on state
        if self.is_active:
            self.image = self.sand_img
        else:
            self.image = self.mud_img
        
        # Update mask for collision detection
        self.mask = pygame.mask.from_surface(self.image)
        
        # Apply shift if provided
        self.rect.x += shift
    
    def draw(self, window, offset_x):
        """Draw the sand"""
        sand_x = self.rect.x - offset_x
        sand_y = self.rect.y
        window.blit(self.image, (sand_x, sand_y))
    
    def collide(self, player):
        """Check collision with player"""
        return self.rect.colliderect(player.rect)
    
    def get_damage(self):
        """Return damage when player touches sand"""
        return 1  # Sand always damages
