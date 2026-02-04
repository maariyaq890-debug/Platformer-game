import os
import random
import math
import pygame
import cv2
from os import listdir
from os.path import isfile, join
from assets.Traps.spikehead import SpikeHead
from assets.Traps.falling_platform import FallingPlatform
from assets.Items.coin import Coin
from sound_manager import SoundManager
from assets.Traps.arrow import Arrow
from assets.Traps.spike import Spike


# Import level modules

pygame.init()
music_on = True
sound_on = True
font = pygame.font.SysFont("arial", 24)  # You can change size/style
pygame.display.set_caption("Platformer")
WIDTH, HEIGHT = 800, 650
FPS = 60
PLAYER_VEL = 6

window = pygame.display.set_mode((WIDTH, HEIGHT))

def load_levels(folder="assets/Menu/Levels"):
    levels = []
    files = sorted(os.listdir(folder))

    for filename in files:
        if filename.endswith(".png"):
            path = join(folder, filename)
            img = pygame.image.load(path).convert_alpha()
            levels.append(img)

    return levels


def draw_button(window, image, pos, mouse_pos, scale=2):
    image_scaled = pygame.transform.scale_by(image, scale)
    rect = image_scaled.get_rect(center=pos)
    
    # Hover effect: scale up slightly
    if rect.collidepoint(mouse_pos):
        image_scaled = pygame.transform.scale_by(image, scale * 1.1)
        rect = image_scaled.get_rect(center=pos)

    window.blit(image_scaled, rect)
    return rect

def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]
def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites


def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)

def get_block_type(size, block_type="default"):
    """Get different block types from the Terrain sprite sheet"""
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    
    # Different block positions in the sprite sheet
    block_positions = {
        "default": (96, 0),      # Original block
        "grass": (0, 0),         # Grass block
        "stone": (192, 0),       # Stone block
        "dirt": (288, 0),        # Dirt block
        "wood": (384, 0),        # Wood block
        "sand": (480, 0),        # Sand block
        "ice": (576, 0),         # Ice block
        "lava": (672, 0),        # Lava block
    }
    
    x, y = block_positions.get(block_type, block_positions["default"])
    rect = pygame.Rect(x, y, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "MaskDude", 32, 32, True)
    ANIMATION_DELAY = 3
    MAX_HEALTH = 5

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.hit_timer = 0
        self.coins = 0

        self.health = self.MAX_HEALTH  
        
        self.sprite = self.SPRITES["idle_right"][0]
        self.image = self.sprite# ✅ This line now works!

    def increase_health(self):
        if self.health < self.MAX_HEALTH:
            self.health += 1

    def decrease_health(self):
        if not self.hit and self.health > 0:
            print("🔥 Player got hit!")
            self.make_hit()
            self.health -= 1
            print("Player health decreased to:", self.health)


    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        if not self.hit:
            self.hit = True
            self.hit_timer = 30

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0
        

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.image = self.sprite
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)
        if self.hit:
            self.hit_timer -= 1
        if self.hit_timer <= 0:
            self.hit = False

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))


class Checkpoint:
    def __init__(self, x, y, idle_image, pressed_sheet, pressed_frames=6, name="checkpoint"):
        self.x = x
        self.y = y
        self.idle_image = idle_image
        self.pressed_sheet = pressed_sheet
        self.pressed_frames = pressed_frames
        self.image = self.idle_image
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.active = False
        self.name = name
        self.animation_count = 0
        self.pressed_images = []
        # Slice the pressed sprite sheet
        frame_width = self.pressed_sheet.get_width() // self.pressed_frames
        frame_height = self.pressed_sheet.get_height()
        for i in range(self.pressed_frames):
            rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
            self.pressed_images.append(self.pressed_sheet.subsurface(rect))

    def activate(self):
        self.active = True
        self.animation_count = 0

    def loop(self):
        if self.active:
            # Animate pressed sprite sheet
            frame = (self.animation_count // 5) % self.pressed_frames
            self.image = self.pressed_images[frame]
            self.animation_count += 1
        else:
            self.image = self.idle_image

    def draw(self, win, offset_x):
        draw_x = self.x - offset_x
        win.blit(self.image, (draw_x, self.y))

class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Block(Object):
    def __init__(self, x, y, size, block_type="default"):
        super().__init__(x, y, size, size)
        block = get_block_type(size, block_type)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        
        self.image = self.fire["off"][0] 
        self.mask = pygame.mask.from_surface(self.image)     # Scale images to the specified size
        self.animation_count = 0
        self.animation_name = "on"  # Always start in off state
        self.name = "fire"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1
        self.update()

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

    def collide(self, player):
        """Check collision with player"""
        return self.rect.colliderect(player.rect)
    
    def get_damage(self):
        """Return damage when player touches fire"""
        return 1


def get_background(name):
    print(f"🎨 Loading background: {name}")
    try:
        image = pygame.image.load(join("assets", "Background", name))
        _, _, width, height = image.get_rect()
        tiles = []

        for i in range(WIDTH // width + 1):
            for j in range(HEIGHT // height + 1):
                pos = (i * width, j * height)
                tiles.append(pos)

        return tiles, image
    except pygame.error as e:
        print(f"⚠️ Error loading background '{name}': {e}")
        # Try fallback to Blue.jpg
        try:
            fallback_name = "Blue.png" if name != "Blue.png" else "Pink.png"
            print(f"🔄 Trying fallback background: {fallback_name}")
            image = pygame.image.load(join("assets", "Background", fallback_name))
            _, _, width, height = image.get_rect()
            tiles = []

            for i in range(WIDTH // width + 1):
                for j in range(HEIGHT // height + 1):
                    pos = (i * width, j * height)
                    tiles.append(pos)

            return tiles, image
        except pygame.error as e2:
            print(f"❌ Fallback background also failed: {e2}")
            # Create a simple colored background as last resort
            image = pygame.Surface((WIDTH, HEIGHT))
            image.fill((100, 150, 255))  # Light blue background
            tiles = [(0, 0)]
            return tiles, image
 



def draw(window, background, bg_image, player, objects, offset_x, coin_count):
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x)
    draw_health(window, player)


    pygame.display.update()

def draw_health(window, player):
    heart_img = pygame.image.load("assets/UI/heart.png").convert_alpha()
    heart_img = pygame.transform.scale(heart_img, (32, 32))
    for i in range(player.health):
        window.blit(heart_img, (10 + i * 36, 10))  # Spaced horizontally

def draw_coins(window, player):
    # Load coin image for the counter
    try:
        # Load the single coin image
        coin_frame = pygame.image.load("assets/Items/Fruits/Coins.png").convert_alpha()
        # Scale to desired size for counter
        coin_frame = pygame.transform.scale(coin_frame, (24, 24))
    except pygame.error:
        # Fallback coin icon
        coin_frame = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.circle(coin_frame, (255, 255, 0), (12, 12), 12)
    
    # Draw coin icon
    window.blit(coin_frame, (10, 50))
    
    # Draw coin count
    font = pygame.font.SysFont("arial", 20)
    coin_text = font.render(f"x {player.coins}", True, (255, 255, 255))
    window.blit(coin_text, (40, 50))

    
def loop_all_objects(objects):
    for obj in objects:
        if hasattr(obj, "loop"):
            obj.loop()


  

def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects


def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object


def handle_move(player, objects):
    keys = pygame.key.get_pressed()
    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]

    for obj in to_check:
        if isinstance(obj, Checkpoint):
            continue
        if getattr(obj, "name", "") in ["fire", "fire2", "spikehead", "spikehead2", "arrow1", "arrow2", "spike1", "spike2", "saw1", "saw2", "rock_head1", "rock_head2", "falling_trap1", "falling_trap2"] and not player.hit:
            player.y_vel = -PLAYER_VEL * 2
            player.decrease_health()

    for obj in to_check:
        name = getattr(obj, "name", None)
        if name in ["fire", "fire2", "spikehead", "spikehead2", "arrow1", "arrow2", "spike1", "spike2", "saw1", "saw2", "rock_head1", "rock_head2", "falling_trap1", "falling_trap2"] and not player.hit:
            player.decrease_health()
            player.y_vel = -PLAYER_VEL * 2

#fire class end
def load_image(path, scale=2):
    image = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale_by(image, scale)

def draw_button_with_label(window, image, pos, label_text, font, mouse_pos):
    x, y = pos
    rect = image.get_rect(center=(x, y))
    window.blit(image, rect)

    # Change label color if hovered
    if rect.collidepoint(mouse_pos):
        label = font.render(label_text, True, (255, 255, 0))  # Yellow on hover
    else:
        label = font.render(label_text, True, (255, 255, 255))

    label_rect = label.get_rect(center=(x, y + image.get_height() // 2 + 20))
    window.blit(label, label_rect)

    return rect

def settings_menu(window):
    clock = pygame.time.Clock()
    run = True

    # Slider values (0 to 100)
    music_volume = 50
    sfx_volume = 50

    # Toggles
    music_on = True
    sfx_on = True
    fullscreen_on = False
    show_fps = False

    # Slider rects
    music_slider_rect = pygame.Rect(200, 130, 200, 10)
    sfx_slider_rect = pygame.Rect(200, 200, 200, 10)

    slider_knob_radius = 10
    font = pygame.font.SysFont("arial", 28)

    # Load icons (ensure these images exist in the folder)
    try:
        music_icon = pygame.transform.scale(pygame.image.load("assets/Menu/Icons/music_icon.png"), (40, 40))
        sfx_icon = pygame.transform.scale(pygame.image.load("assets/Menu/Icons/sfx_icon.png"), (40, 40))
        back_icon = pygame.transform.scale(pygame.image.load("assets/Menu/Buttons/Back.png"), (60, 60))
    except:
        print("⚠ Missing icons in 'assets/Menu/Icons/' or 'Buttons/'. Using placeholders.")
        music_icon = sfx_icon = back_icon = pygame.Surface((40, 40))
        music_icon.fill((255, 100, 100))
        sfx_icon.fill((100, 255, 100))
        back_icon = pygame.Surface((60, 60))
        back_icon.fill((100, 100, 255))

    back_rect = back_icon.get_rect(topleft=(10, 10))

    while run:
        clock.tick(60)
        window.fill((40, 40, 70))

        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()[0]

        # Draw sliders and icons
        window.blit(music_icon, (150, 120))
        window.blit(sfx_icon, (150, 190))

        # Draw slider bars
        pygame.draw.rect(window, (200, 200, 200), music_slider_rect)
        pygame.draw.circle(window, (255, 255, 255), (music_slider_rect.x + int(music_volume * 2), music_slider_rect.y + 5), slider_knob_radius)

        pygame.draw.rect(window, (200, 200, 200), sfx_slider_rect)
        pygame.draw.circle(window, (255, 255, 255), (sfx_slider_rect.x + int(sfx_volume * 2), sfx_slider_rect.y + 5), slider_knob_radius)

        # Draw Toggles
        def draw_toggle(label, y, state):
            text = font.render(label, True, (255, 255, 255))
            window.blit(text, (150, y))
            toggle_color = (0, 200, 0) if state else (200, 0, 0)
            rect = pygame.Rect(400, y + 5, 50, 25)
            pygame.draw.rect(window, toggle_color, rect)
            return rect

        music_toggle = draw_toggle("Music:", 270, music_on)
        sfx_toggle = draw_toggle("Sound Effects:", 320, sfx_on)
        fullscreen_toggle = draw_toggle("Fullscreen:", 370, fullscreen_on)
        fps_toggle = draw_toggle("Show FPS:", 420, show_fps)

        # Draw Back Button
        window.blit(back_icon, back_rect)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if back_rect.collidepoint((mx, my)):
                    run = False  # Go back to main menu



                # Slider logic
                if music_slider_rect.collidepoint((mx, my)):
                    music_volume = min(max((mx - music_slider_rect.x) // 2, 0), 100)

                if sfx_slider_rect.collidepoint((mx, my)):
                    sfx_volume = min(max((mx - sfx_slider_rect.x) // 2, 0), 100)

                # Toggle logic
                if music_toggle.collidepoint((mx, my)):
                    music_on = not music_on
                if sfx_toggle.collidepoint((mx, my)):
                    sfx_on = not sfx_on
                if fullscreen_toggle.collidepoint((mx, my)):
                    fullscreen_on = not fullscreen_on
                if fps_toggle.collidepoint((mx, my)):
                    show_fps = not show_fps

def restart_game(window):
    print("Restarting game...")
    main(window)  # Or however you load your game/level

def main_menu(window):
    run = True  # <--- THIS MUST BE HERE
    clock = pygame.time.Clock()
    
    # Initialize sound manager for menu
    sound_manager = SoundManager()
    sound_manager.play_music("menu_music.mp3")

    # Load background image
    bg_image = pygame.image.load(join("assets", "Menu", "background.jpg")).convert()
    bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))

    # Load all button images
    play_btn = pygame.image.load(join("assets", "Menu", "Buttons", "Play.png")).convert_alpha()
    back_btn = pygame.image.load(join("assets", "Menu", "Buttons", "Back.png")).convert_alpha()
    close_btn = pygame.image.load(join("assets", "Menu", "Buttons", "Close.png")).convert_alpha()
    next_btn = pygame.image.load(join("assets", "Menu", "Buttons", "Next.png")).convert_alpha()
    prev_btn = pygame.image.load(join("assets", "Menu", "Buttons", "Previous.png")).convert_alpha()
    restart_btn = pygame.image.load(join("assets", "Menu", "Buttons", "Restart.png")).convert_alpha()
    settings_btn = pygame.image.load(join("assets", "Menu", "Buttons", "Settings.png")).convert_alpha()


    title_font = pygame.font.SysFont("lucidaconsole", 70)
    label_font = pygame.font.SysFont("terminal", 22)
    title_text = title_font.render("Platformer", True, (255, 255, 255))


    

    while run:
        clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()

        # Draw background instead of solid color
        window.blit(bg_image, (0, 0))

        window.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 5))

        # Draw all buttons
        play_rect = draw_button_with_label(window, play_btn, (WIDTH // 2, HEIGHT // 2 - 30), "Play", label_font, mouse_pos)
        procedural_rect = draw_button_with_label(window, play_btn, (WIDTH // 2, HEIGHT // 2 + 60), "Procedural Levels", label_font, mouse_pos)
        settings_rect = draw_button_with_label(window, settings_btn, (WIDTH // 2, HEIGHT // 2 + 150), "Settings", label_font, mouse_pos)
        restart_rect = draw_button_with_label(window, restart_btn, (WIDTH // 2, HEIGHT // 2 + 240), "Restart", label_font, mouse_pos)

        back_rect = draw_button_with_label(window, back_btn, (WIDTH // 2 - 180, HEIGHT - 80), "Back", label_font, mouse_pos)
        prev_rect = draw_button_with_label(window, prev_btn, (WIDTH // 2 - 90, HEIGHT - 80), "Previous", label_font, mouse_pos)
        next_rect = draw_button_with_label(window, next_btn, (WIDTH // 2 + 90, HEIGHT - 80), "Next", label_font, mouse_pos)
        close_rect = draw_button_with_label(window, close_btn, (WIDTH // 2 + 180, HEIGHT - 80), "Close", label_font, mouse_pos)

        
        
        
        pygame.display.update()



        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

            # ✅ All event.pos checks must be inside this block
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_rect.collidepoint(event.pos):
                    sound_manager.play_sound('button_click')
                    run = False  # Start game

                elif procedural_rect.collidepoint(event.pos):
                    sound_manager.play_sound('button_click')
                    try:
                        from procedural_levels import start_procedural_levels
                        start_procedural_levels(window)
                        return  # Return to main menu after procedural levels
                    except ImportError:
                        print("⚠️ Procedural levels module not found")
                        run = False

                elif next_rect.collidepoint(event.pos):
                    sound_manager.play_sound('button_click')
                    level_menu(window)  # Show level selection

                elif close_rect.collidepoint(event.pos):
                    sound_manager.play_sound('button_click')
                    pygame.quit()
                    quit()

                elif settings_rect.collidepoint(event.pos):
                    sound_manager.play_sound('button_click')
                    settings_menu(window)

                elif restart_rect.collidepoint(event.pos):
                    sound_manager.play_sound('button_click')
                    restart_game(window)

                elif back_rect.collidepoint(event.pos):
                    sound_manager.play_sound('button_click')
                    print("Back clicked (no action yet)")

                elif prev_rect.collidepoint(event.pos):
                    sound_manager.play_sound('button_click')
                    print("Previous clicked (no action yet)")

def level_menu(window):
    clock = pygame.time.Clock()
    run = True
    levels = load_levels()
    

    level_rects = []
    current_page = 0
    levels_per_page = 20
    columns = 5
    rows = 4
    gap = 20
    box_size = 80

    back_button = pygame.image.load(join("assets", "Menu", "Buttons", "Back.png")).convert_alpha()
    # Load button images
    prev_button = pygame.image.load("assets/Menu/Buttons/Previous.png").convert_alpha()
    next_button = pygame.image.load("assets/Menu/Buttons/Next.png").convert_alpha()
    back_button = pygame.image.load("assets/Menu/Buttons/Back.png").convert_alpha()

    # Scale buttons
    prev_button = pygame.transform.scale(prev_button, (50, 50))
    next_button = pygame.transform.scale(next_button, (50, 50))
    back_button = pygame.transform.scale(back_button, (50, 50))

    # Button positions
    prev_rect = prev_button.get_rect(topleft=(40, 350))
    next_rect = next_button.get_rect(topleft=(580, 350))
    back_rect = back_button.get_rect(topleft=(10, 10))

    def draw_levels():
        window.fill((20, 20, 50))
        start_index = current_page * levels_per_page
        end_index = min(start_index + levels_per_page, len(levels))
        level_rects.clear()

        for i, level_image in enumerate(levels[start_index:end_index]):
            row = i // columns
            col = i % columns
            x = 100 + col * (box_size + gap)
            y = 100 + row * (box_size + gap)
            level_image = pygame.transform.scale(level_image, (box_size, box_size))
            rect = level_image.get_rect(topleft=(x, y))
            window.blit(level_image, rect)
            level_rects.append((rect, start_index + i))


            
        # Draw buttons
        window.blit(prev_button, prev_rect)
        window.blit(next_button, next_rect)
        window.blit(back_button, back_rect)

        pygame.display.update()

    while run:
        clock.tick(60)
        draw_levels()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if prev_rect.collidepoint(mouse_pos) and current_page > 0:
                    current_page -= 1
                elif next_rect.collidepoint(mouse_pos) and (current_page + 1) * levels_per_page < len(levels):
                    current_page += 1
                elif back_rect.collidepoint(mouse_pos):
                    run = False  # Back to menu
                    main_menu(window)
                else:
                    for rect, level_num in level_rects:
                        if rect.collidepoint(mouse_pos):
                            print(f"✅ Level {level_num:02} selected!")
                            # 🎮 Start the game with selected level (pass it to main)
                            main(window, level_num)
                            run = False
                            break
def show_game_over(window):
    """Play Game Over video with sound and buttons (Play Again / Exit)."""
    clock = pygame.time.Clock()
    run = True

    # Start music
    sound_manager = SoundManager()
    sound_manager.play_music("gameover.mp3", loop=False)

    # Open video
    cap = cv2.VideoCapture("assets/gameover.mp4")
    if not cap.isOpened():
        print("⚠️ Error: Could not open gameover.mp4")
        return

    # Fonts
    button_font = pygame.font.SysFont("comicsans", 40)

    # Button setup
    button_width, button_height = 250, 60
    spacing = 20
    play_again_rect = pygame.Rect(WIDTH // 2 - button_width // 2, HEIGHT // 2 + 100, button_width, button_height)
    exit_rect = pygame.Rect(WIDTH // 2 - button_width // 2, HEIGHT // 2 + 100 + button_height + spacing, button_width, button_height)

    while run:
        ret, frame = cap.read()
        if not ret:
            # Restart video loop if ended
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = cap.read()

        # Convert BGR → RGB → Surface
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (WIDTH, HEIGHT))
        surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        window.blit(surface, (0, 0))

        # Mouse hover
        mx, my = pygame.mouse.get_pos()
        play_hover = play_again_rect.collidepoint(mx, my)
        exit_hover = exit_rect.collidepoint(mx, my)

        play_color = (0, 220, 0) if play_hover else (0, 180, 0)
        exit_color = (220, 0, 0) if exit_hover else (180, 0, 0)

        # Draw buttons
        pygame.draw.rect(window, play_color, play_again_rect, border_radius=10)
        pygame.draw.rect(window, exit_color, exit_rect, border_radius=10)

        # Button text
        play_text = button_font.render("Play Again", True, (255, 255, 255))
        exit_text = button_font.render("Exit", True, (255, 255, 255))
        window.blit(play_text, play_text.get_rect(center=play_again_rect.center))
        window.blit(exit_text, exit_text.get_rect(center=exit_rect.center))

        pygame.display.update()
        clock.tick(30)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cap.release()
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_hover:
                    cap.release()
                    sound_manager.stop_music()
                    return  # Restart game
                elif exit_hover:
                    cap.release()
                    sound_manager.stop_music()
                    pygame.quit()
                    exit()

    cap.release()
    sound_manager.stop_music()
    return


def main(window, level_num=0):
    print(f"🌟 Starting Level {level_num}")
    clock = pygame.time.Clock()
    background, bg_image = get_background("Brown.jpg")
    
    # Initialize sound manager
    sound_manager = SoundManager()
    sound_manager.play_music("background_music.mp3")

    block_size = 96
    player = Player(100, HEIGHT - block_size * 2 - 50, 50, 50)
    player.sound_manager = sound_manager  # Pass sound manager to player

    fire = Fire(800, HEIGHT - block_size - 64, 16, 32)
    fire.name = "fire"
    fire2 = Fire(900, HEIGHT - block_size - 64, 16, 32)
    fire2.name = "fire2"
    fire3 = Fire(1000, HEIGHT - block_size - 64, 16, 32)
    fire3.name = "fire3"
    spikehead = SpikeHead(700, 500)
    spikehead2 = SpikeHead(1700, 500)
    falling1 = FallingPlatform(900, 200)
    falling2 = FallingPlatform(2200, 200)

    floor = [Block(I * block_size, HEIGHT - block_size, block_size)
             for I in range(-WIDTH // block_size, (WIDTH * 2) // block_size)]

    block_with_fire = Block(block_size * 4, HEIGHT - block_size * 4, block_size)
    fire = Fire(
        block_with_fire.rect.x + (block_with_fire.rect.width - 16) // 2,
        block_with_fire.rect.y - 62,
        16, 32
    )
    fire.name = "fire"

    block_with_fire2 = Block(block_size * 11, HEIGHT - block_size * 2, block_size)
    fire2 = Fire(
        block_with_fire2.rect.x + (block_with_fire2.rect.width - 16) // 2,
        block_with_fire2.rect.y - 62,
        16, 32
    )
    fire2.name = "fire2"

    block_with_fire3 = Block(block_size * 22, HEIGHT - block_size * 1, block_size)
    fire3 = Fire(
        block_with_fire3.rect.x + (block_with_fire3.rect.width - 16) // 2,
        block_with_fire3.rect.y - 62,
        16, 32
    )
    fire3.name = "fire3"

    # Add coins to the tutorial level
    coins = [
        Coin(block_size * 6, HEIGHT - block_size * 3 - 50),
        Coin(block_size * 9, HEIGHT - block_size * 4 - 50),
        Coin(block_size * 13, HEIGHT - block_size * 3 - 50),
        Coin(block_size * 17, HEIGHT - block_size * 2 - 50),
        Coin(block_size * 21, HEIGHT - block_size * 2 - 50),
        Coin(block_size * 25, HEIGHT - block_size * 2 - 50),
    ]

    objects = [
        *floor,
        Block(0, HEIGHT - block_size * 2, block_size),
        Block(0, HEIGHT - block_size * 3, block_size),
        Block(0, HEIGHT - block_size * 4, block_size),
        Block(0, HEIGHT - block_size * 5, block_size),
        Block(0, HEIGHT - block_size * 6, block_size),
       
        block_with_fire,
        Block(block_size * 3, HEIGHT - block_size * 3, block_size),
        Block(block_size * 5, HEIGHT - block_size * 4, block_size),
        Block(block_size * 8, HEIGHT - block_size * 4, block_size),
        block_with_fire2,
        Block(block_size * 12, HEIGHT - block_size * 2, block_size),
        Block(block_size * 12, HEIGHT - block_size * 3, block_size),
        Block(block_size * 14, HEIGHT - block_size * 4, block_size),
        Block(block_size * 15, HEIGHT - block_size * 5, block_size),
        Block(block_size * 16, HEIGHT - block_size * 5, block_size),
        Block(block_size * 16, HEIGHT - block_size * 1, block_size),
        Block(block_size * 17, HEIGHT - block_size * 1, block_size),
        Block(block_size * 18, HEIGHT - block_size * 1, block_size),
        Block(block_size * 18, HEIGHT - block_size * 4, block_size),
        Block(block_size * 19, HEIGHT - block_size * 1, block_size),
        Block(block_size * 19, HEIGHT - block_size * 5, block_size),
        Block(block_size * 20, HEIGHT - block_size * 1, block_size),
        Block(block_size * 20, HEIGHT - block_size * 5, block_size),
        Block(block_size * 21, HEIGHT - block_size * 1, block_size),
        block_with_fire3,
        Block(block_size * 23, HEIGHT - block_size * 1, block_size),
        Block(block_size * 23, HEIGHT - block_size * 2, block_size),
        Block(block_size * 24, HEIGHT - block_size * 1, block_size),
        Block(block_size * 24, HEIGHT - block_size * 2, block_size),
        Block(block_size * 25, HEIGHT - block_size * 1, block_size),
        Block(block_size * 26, HEIGHT - block_size * 1, block_size),
        Block(block_size * 27, HEIGHT - block_size * 1, block_size),
        Block(block_size * 28, HEIGHT - block_size * 1, block_size),
        Block(block_size * 29, HEIGHT - block_size * 1, block_size),
        Block(block_size * 29, HEIGHT - block_size * 2, block_size),
        Block(block_size * 29, HEIGHT - block_size * 3, block_size),
        Block(block_size * 29, HEIGHT - block_size * 4, block_size),
        Block(block_size * 29, HEIGHT - block_size * 5, block_size),
        Block(block_size * 29, HEIGHT - block_size * 6, block_size),
       
        
        fire,
        fire2,
        fire3,
        spikehead,
        spikehead2,
    ]
    
    offset_x = 0
    scroll_area_width = 200
    run = True

    # Add end checkpoint at the far right of the level
    end_idle_img = pygame.image.load("assets/Items/Checkpoints/End/end_idle.png").convert_alpha()
    end_pressed_sheet = pygame.image.load("assets/Items/Checkpoints/End/end_pressed.png").convert_alpha()
    end_checkpoint = Checkpoint(2600, HEIGHT - block_size - 80, end_idle_img, end_pressed_sheet, pressed_frames=6, name="end_checkpoint")
    objects.append(end_checkpoint)

    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()
                    

        if player.health <= 0:
            sound_manager.play_sound('death')
            show_game_over(window)
            print("Player Health:", player.health)
            return main(window)

        player.loop(FPS)  # Apply gravity and move
        fire.loop()
        fire2.loop()
        fire3.loop()
        handle_move(player, objects)  # Handle collisions

       

        falling1.collide(player)
        falling2.collide(player)
        loop_all_objects(objects)

        spikehead.update(player)
        spikehead2.update(player)
        falling1.update(player)
        falling2.update(player)
        
        # Handle coin collection
        for coin in coins:
            coin.update()
            if coin.collide(player):
                if not hasattr(player, 'coins'):
                    player.coins = 0
                player.coins += 1
                sound_manager.play_sound('coin_collect')
                print(f"🪙 Coin collected! Total coins: {player.coins}")
        
        draw(window, background, bg_image, player, objects, offset_x, 0)
        spikehead.draw(window, offset_x)
        spikehead2.draw(window, offset_x)
        falling1.draw(window, offset_x)
        falling2.draw(window, offset_x)
        
        # Draw coins
        for coin in coins:
            coin.draw(window, offset_x)
            
        draw_health(window, player)
        draw_coins(window, player)

 

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
            (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel

        pygame.display.update()

        # Check for end checkpoint collision
        if pygame.sprite.collide_rect(player, end_checkpoint):
            end_checkpoint.activate()
            sound_manager.play_sound('checkpoint')
            show_victory(window)
            # Show level complete message


def show_victory(window):
    """Play a victory video with sound until it ends or player presses any key"""
    clock = pygame.time.Clock()
    run = True

    # Play victory sound/music
    pygame.mixer.music.load("victory.mp3")
    pygame.mixer.music.play()

    # Open video with OpenCV
    cap = cv2.VideoCapture("assets/victory.mp4")
    if not cap.isOpened():
        print("Error: Could not open victory video.")
        return

    while run:
        ret, frame = cap.read()
        if not ret:
            # Video ended
            break

        # Handle quit/key press FIRST
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cap.release()
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                cap.release()
                pygame.mixer.music.stop()
                pygame.quit()
                exit()

        # Convert from BGR (OpenCV) to RGB (Pygame)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (WIDTH, HEIGHT))  # match your game window size

        # Convert to pygame surface
        surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        window.blit(surface, (0, 0))
        pygame.display.update()

        # Limit FPS
        clock.tick(30)

    # Cleanup when video ends
    cap.release()
    pygame.mixer.music.stop()
    pygame.quit()
    exit()

if __name__ == "__main__":
    main_menu(window)
    main(window, 0)  

    import pygame  # Start with Level 0 (tutorial)

