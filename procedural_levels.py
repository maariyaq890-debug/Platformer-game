import pygame
import random
import cv2
from main import *
from assets.Traps.saw import Saw
from assets.Traps.rock_head import RockHead
from assets.Traps.arrow import Arrow
from assets.Traps.spike import Spike
from assets.Traps.spikehead import SpikeHead
from assets.Traps.fan import Fan
from assets.Traps.sand import Sand
from assets.Items.coin import Coin
from sound_manager import SoundManager

class ProceduralLevelGenerator:
    def __init__(self):
        self.block_size = 96
        self.seed = 0
        self.difficulty = 1
        
    def set_seed(self, seed):
        
        self.seed = seed
        random.seed(seed)
        
    def set_difficulty(self, difficulty):
        
        self.difficulty = max(1, min(5, difficulty))
        
    def generate_terrain(self, level_width):
        
        blocks = []
        
    
        floor_blocks = [Block(x * self.block_size, HEIGHT - self.block_size, 
                             self.block_size, "grass") 
                       for x in range(-WIDTH // self.block_size, 
                                    level_width // self.block_size)]
        blocks.extend(floor_blocks)
        
        
        platform_count = 3 + self.difficulty * 2 
        
        
        used_positions = set()
        
       
        section_width = level_width // (platform_count + 1)
        
        for i in range(platform_count):
            attempts = 0
            while attempts < 100:  
                
                section_start = 200 + (i * section_width)
                section_end = section_start + section_width - 100
                
                x = random.randint(section_start, section_end)
                y = random.randint(HEIGHT - self.block_size * 5, HEIGHT - self.block_size * 2)
                width = random.randint(1, 3)  
                
                
                position_key = (x // self.block_size, y // self.block_size)
                
               
                buffer_zone_clear = True
                for dx in range(-1, width + 1):  
                    for dy in range(-1, 2): 
                        check_x = (x + dx * self.block_size) // self.block_size
                        check_y = (y + dy * self.block_size) // self.block_size
                        if (check_x, check_y) in used_positions:
                            buffer_zone_clear = False
                            break
                    if not buffer_zone_clear:
                        break
                
                if buffer_zone_clear:
                    
                    for j in range(width):
                        used_positions.add(((x + j * self.block_size) // self.block_size, y // self.block_size))
                    
                    
                    for j in range(width):
                        block_type = random.choice([ "dirt","stone", "wood"])
                        blocks.append(Block(x + j * self.block_size, y, 
                                          self.block_size, block_type))
                    break
                attempts += 1
        
        
        floating_count = 2 + self.difficulty  
        for i in range(floating_count):
            attempts = 0
            while attempts < 100:
               
                section_start = 300 + (i * (level_width - 600) // (floating_count + 1))
                section_end = section_start + 200
                
                x = random.randint(section_start, section_end)
                y = random.randint(HEIGHT - self.block_size * 8, HEIGHT - self.block_size * 3)
                
               
                position_key = (x // self.block_size, y // self.block_size)
                
               
                buffer_zone_clear = True
                for dx in range(-2, 3):  
                    for dy in range(-2, 3):  
                        check_x = (x + dx * self.block_size) // self.block_size
                        check_y = (y + dy * self.block_size) // self.block_size
                        if (check_x, check_y) in used_positions:
                            buffer_zone_clear = False
                            break
                    if not buffer_zone_clear:
                        break
                
                if buffer_zone_clear:
                    used_positions.add(position_key)
                    block_type = random.choice([ "dirt","stone", "wood", "grass", "sand", "ice", "lava"])
                    blocks.append(Block(x, y, self.block_size, block_type))
                    break
                attempts += 1
        
        return blocks, used_positions
        
    def generate_traps(self, level_width, used_positions):
        
        traps = []
        
       
        trap_count = min(3 + self.difficulty // 2, 8)  
        print(f"🎯 Generating {trap_count} traps for level...")
        
       
        trap_types = [
            ("arrow", Arrow),
            ("spike", Spike),
            ("fire", Fire),
            ("spikehead", SpikeHead),
            ("saw", Saw),  
            ("rock_head", RockHead), 
            ("fan", Fan),  
            ("sand", Sand),  
        ]
        
        
        trap_positions = set()
        
       
        trap_type_count = {trap_name: 0 for trap_name, _ in trap_types}
        
        for i in range(trap_count):
            attempts = 0
            while attempts < 100:  
                x = random.randint(300, level_width - 300)
                y = HEIGHT - self.block_size - 60 
                
                
                position_key = x // 250  
                if position_key not in trap_positions:
                    
                    trap_x_grid = x // self.block_size
                    trap_y_grid = y // self.block_size
                    
                   
                    block_collision = False
                    for dx in range(-1, 2): 
                        for dy in range(-1, 2):
                            check_pos = (trap_x_grid + dx, trap_y_grid + dy)
                            if check_pos in used_positions:
                                block_collision = True
                                break
                        if block_collision:
                            break
                    
                    if not block_collision:
                       
                        available_traps = [(name, trap_class) for name, trap_class in trap_types 
                                         if trap_type_count[name] < 2]
                        
                        if available_traps:
                            
                            if "sand" in [name for name, _ in available_traps] and trap_type_count["sand"] < 1:
                                trap_name, trap_class = ("sand", Sand)
                            elif "fan" in [name for name, _ in available_traps] and trap_type_count["fan"] < 1:
                                trap_name, trap_class = ("fan", Fan)
                            elif "spikehead" in [name for name, _ in available_traps] and trap_type_count["spikehead"] < 1:
                                trap_name, trap_class = ("spikehead", SpikeHead)
                            else:
                                trap_name, trap_class = random.choice(available_traps)
                            trap_type_count[trap_name] += 1
                            
                            try:
                                if trap_name == "fire":
                                    
                                    trap = Fire(x, y + 20, 32, 32) 
                                    trap.on()  
                                    trap.name = f"fire{trap_type_count[trap_name]}"
                                elif trap_name == "spikehead":
                                   
                                    trap = SpikeHead(x, y + 40)
                                    trap.name = f"spikehead{trap_type_count[trap_name]}"
                                elif trap_name == "saw":
                                   
                                    trap = Saw(x, y + 30)  
                                    trap.name = f"saw{trap_type_count[trap_name]}"
                                elif trap_name == "rock_head":
                                    
                                    trap = RockHead(x, y + 50)  
                                    trap.name = f"rock_head{trap_type_count[trap_name]}"
                                elif trap_name == "fan":
                                    
                                    trap = Fan(x, 510)  
                                    trap.name = f"fan{trap_type_count[trap_name]}"
                                elif trap_name == "sand":
                                    
                                    trap = Sand(x, 510)  
                                    trap.name = f"sand{trap_type_count[trap_name]}"
                                else:
                                    # Arrow and Spike use standard positioning
                                    if trap_name == "arrow":
                                        # Arrow traps positioned higher for better visibility
                                        trap = trap_class(x, y + 25)
                                    else:
                                        trap = trap_class(x, y)
                                    trap.name = f"{trap_name}{trap_type_count[trap_name]}"
                                
                                traps.append(trap)
                                trap_positions.add(position_key)
                                print(f"✅ Created {trap_name} trap at ({x}, {trap.rect.y})")
                                break
                            except Exception as e:
                                print(f"⚠️ Error creating {trap_name} trap: {e}")
                                attempts += 1
                                continue
                attempts += 1
        
        return traps
        
    def generate_falling_platforms(self, level_width, used_positions):
        """Generate falling platforms with better variety and positioning - NO OVERLAP"""
        platforms = []
        
        # More falling platforms for variety but still performance-optimized
        platform_count = min(2 + self.difficulty, 3)  # Max 3 platforms
        
        # Track positions to prevent clustering and overlap
        used_platform_positions = set()
        
        for i in range(platform_count):
            attempts = 0
            while attempts < 100:
                x = random.randint(400, level_width - 400)
                y = random.randint(150, 300)  # More height variety
                
                # Check if platform is too close to another
                position_key = x // 300  # Group positions every 300 pixels
                if position_key not in used_platform_positions:
                    # Check if platform overlaps with blocks
                    platform_x_grid = x // self.block_size
                    platform_y_grid = y // self.block_size
                    
                    block_collision = False
                    for dx in range(-1, 2):  # Check 3x3 area around platform
                        for dy in range(-1, 2):
                            check_pos = (platform_x_grid + dx, platform_y_grid + dy)
                            if check_pos in used_positions:
                                block_collision = True
                                break
                        if block_collision:
                            break
                    
                    if not block_collision:
                        used_platform_positions.add(position_key)
                        platforms.append(FallingPlatform(x, y))
                        break
                attempts += 1
        
        return platforms
        
    def generate_coins(self, level_width, used_positions):
        """Generate coins scattered throughout the level"""
        coins = []
        
        # Generate coins based on level difficulty
        coin_count = 5 + self.difficulty * 3  # More coins in higher levels
        
        # Track coin positions to prevent clustering
        coin_positions = set()
        
        for i in range(coin_count):
            attempts = 0
            while attempts < 50:
                x = random.randint(200, level_width - 200)
                y = random.randint(HEIGHT - self.block_size * 6, HEIGHT - self.block_size * 3)
                
                # Check if coin is too close to another coin
                position_key = x // 100  # Group positions every 100 pixels
                if position_key not in coin_positions:
                    # Check if coin position overlaps with blocks
                    coin_x_grid = x // self.block_size
                    coin_y_grid = y // self.block_size
                    
                    # Check if this position or nearby positions are occupied by blocks
                    block_collision = False
                    for dx in range(-1, 2):  # Check 3x3 area around coin
                        for dy in range(-1, 2):
                            check_pos = (coin_x_grid + dx, coin_y_grid + dy)
                            if check_pos in used_positions:
                                block_collision = True
                                break
                        if block_collision:
                            break
                    
                    if not block_collision:
                        coin_positions.add(position_key)
                        coins.append(Coin(x, y))
                        print(f"🪙 Created coin at ({x}, {y})")
                        break
                attempts += 1
        
        return coins
        
    def generate_level(self, window, level_number):
        """Generate a complete procedural level"""
        print(f"🌟 Generating Procedural Level {level_number}!")
        
        # Set seed based on level number for consistency
        self.set_seed(level_number)
        self.set_difficulty(level_number)
        
        clock = pygame.time.Clock()
        
        # Different backgrounds based on level (most converted to JPG, keeping Pink.png)
        backgrounds = ["Blue.png", "Green.png", "Brown.jpg", "Pink.png", "Purple.jpg"]
        bg_name = backgrounds[(level_number - 1) % len(backgrounds)]
        
        try:
            background, bg_image = get_background(bg_name)
        except:
            # Fallback to default if background not found
            background, bg_image = get_background("Blue.png")
        
        # Initialize sound manager after background is loaded
        sound_manager = SoundManager()
        sound_manager.play_music("background_music.mp3")
        
        # Different characters based on level
        characters = ["MaskDude", "NinjaFrog", "VirtualGuy", "PinkMan"]
        char_name = characters[(level_number - 1) % len(characters)]
        
        class DynamicPlayer(Player):
            SPRITES = load_sprite_sheets("MainCharacters", char_name, 32, 32, True)
        
        # Player starting position - FIXED for visibility
        player = DynamicPlayer(100, HEIGHT - self.block_size * 3 - 50, 50, 50)
        player.sound_manager = sound_manager  # Pass sound manager to player
        
        # Ensure player is visible and properly initialized
        player.rect.x = 100
        player.rect.y = HEIGHT - self.block_size * 3 - 50
        player.x = 100
        player.y = HEIGHT - self.block_size * 3 - 50
        
        # Ensure player has proper health
        if not hasattr(player, 'health') or player.health <= 0:
            player.health = 5
        
        
        # Initialize player coins
        if not hasattr(player, 'coins'):
            player.coins = 0
        
        
        # Generate level content
        level_width = 3000 + level_number * 500  # Wider levels for higher difficulties
        
        terrain_blocks, used_positions = self.generate_terrain(level_width)
        traps = self.generate_traps(level_width, used_positions)
        falling_platforms = self.generate_falling_platforms(level_width, used_positions)
        coins = self.generate_coins(level_width, used_positions)
        
        # Combine all objects
        objects = terrain_blocks + traps + falling_platforms
        
        # Ensure Fire traps are in objects list for animation
        for trap in traps:
            if trap.__class__.__name__ == 'Fire':
                if trap not in objects:
                    objects.append(trap)
        
        # Add end checkpoint - ensure it's not inside blocks
        end_idle_img = pygame.image.load("assets/Items/Checkpoints/End/end_idle.png").convert_alpha()
        end_pressed_sheet = pygame.image.load("assets/Items/Checkpoints/End/end_pressed.png").convert_alpha()
        
        # Find a safe position for checkpoint (not inside blocks)
        checkpoint_x = level_width - 200
        checkpoint_y = HEIGHT - self.block_size - 80
        
        # Check if checkpoint position overlaps with blocks
        checkpoint_x_grid = checkpoint_x // self.block_size
        checkpoint_y_grid = checkpoint_y // self.block_size
        
        # If checkpoint is inside a block, find a completely safe position
        if (checkpoint_x_grid, checkpoint_y_grid) in used_positions:
            # Try multiple positions to find a safe spot
            safe_found = False
            for y_offset in range(-3, 4):  # Try different heights
                for x_offset in range(-10, 1):  # Try moving left
                    test_x = checkpoint_x + (x_offset * self.block_size)
                    test_y = checkpoint_y + (y_offset * self.block_size)
                    test_x_grid = test_x // self.block_size
                    test_y_grid = test_y // self.block_size
                    
                    # Check if this position is safe (not in used_positions)
                    if (test_x_grid, test_y_grid) not in used_positions:
                        # Also check surrounding area to ensure it's accessible
                        area_safe = True
                        for dx in range(-1, 2):
                            for dy in range(-1, 2):
                                check_pos = (test_x_grid + dx, test_y_grid + dy)
                                if check_pos in used_positions:
                                    area_safe = False
                                    break
                            if not area_safe:
                                break
                        
                        if area_safe:
                            checkpoint_x = test_x
                            checkpoint_y = test_y
                            safe_found = True
                            break
                if safe_found:
                    break
            
            # If still no safe position found, place it high up in the air
            if not safe_found:
                checkpoint_x = level_width - 200
                checkpoint_y = 100  # High up in the air
        
        end_checkpoint = Checkpoint(checkpoint_x, checkpoint_y, 
                                  end_idle_img, end_pressed_sheet, pressed_frames=6, 
                                  name="end_checkpoint")
        objects.append(end_checkpoint)
        
        # Game loop
        offset_x = 0
        scroll_area_width = 200
        run = True
        
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
                # Restart the current procedural level instead of going back to tutorial
                return self.generate_level(window, level_number)
            
            player.loop(FPS)
            handle_move(player, objects)
            
            # Update all objects including traps for proper animation
            for trap in traps:
                # Handle different trap update signatures
                if hasattr(trap, 'update'):
                    if trap.__class__.__name__ in ['SpikeHead', 'FallingPlatform']:
                        trap.update(player)
                    else:
                        trap.update()
                # Fire uses loop() method for animation
                elif hasattr(trap, 'loop'):
                    trap.loop()
                
                # Play trap activation sounds based on trap type (only when state changes)
                if hasattr(trap, 'is_active'):
                    if not hasattr(trap, 'last_active_state'):
                        trap.last_active_state = trap.is_active
                    elif trap.is_active != trap.last_active_state:
                        # State changed, play sound
                        if trap.is_active:  # Only when activating
                            if trap.__class__.__name__ == 'Fire':
                                sound_manager.play_sound('fire_activate')
                            elif trap.__class__.__name__ == 'Fan':
                                sound_manager.play_sound('fan_activate')
                            elif trap.__class__.__name__ == 'Sand':
                                sound_manager.play_sound('sand_activate')
                        trap.last_active_state = trap.is_active
                
                # Check trap collision with player and damage (with cooldown)
                if hasattr(trap, 'collide') and trap.collide(player):
                    if hasattr(trap, 'get_damage'):
                        damage = trap.get_damage()
                        if damage > 0:
                            # Check if trap has cooldown attribute, if not create it
                            if not hasattr(trap, 'last_damage_time'):
                                trap.last_damage_time = 0
                            
                            current_time = pygame.time.get_ticks()
                            # Only damage if enough time has passed (500ms cooldown)
                            if current_time - trap.last_damage_time > 500:
                                player.health -= damage
                                trap.last_damage_time = current_time
                                sound_manager.play_sound('health_loss')
                               
                
            for platform in falling_platforms:
                platform.collide(player)
                platform.update(player)
            
            # Handle coin collection
            for coin in coins:
                coin.update()
                if coin.collide(player):
                    player.coins += 1
                    sound_manager.play_sound('coin_collect')
                    
                
            # Update all other objects
            loop_all_objects(objects)
            
            # Draw everything
            draw(window, background, bg_image, player, objects, offset_x, 0)
            
            # Draw traps and platforms separately
            for trap in traps:
                trap.draw(window, offset_x)
            for platform in falling_platforms:
                platform.draw(window, offset_x)
            
            # Draw coins
            for coin in coins:
                coin.draw(window, offset_x)
                
            draw_health(window, player)
            draw_coins(window, player)
            
            # Camera scrolling
            if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
                offset_x += player.x_vel
            
            pygame.display.update()
            
            # Check for level completion
            if pygame.sprite.collide_rect(player, end_checkpoint):
                end_checkpoint.activate()
                sound_manager.play_sound('checkpoint')
                sound_manager.play_sound('level_complete')

                image_path = f"assets/level_complete/level{level_number}_complete.png"
                if os.path.exists(image_path):
                    level_image = pygame.image.load(image_path)
                    level_image = pygame.transform.scale(level_image, (WIDTH, HEIGHT))
                else:
                    print(f"⚠️ Image not found: {image_path}, using fallback text.")
                    level_image = None

                font = pygame.font.SysFont("arial", 48)  # make sure font exists
                message_run = True

                while message_run:
                    clock.tick(60)

                    if level_image:
                        window.blit(level_image, (0, 0))
                    else:
                        window.fill((30, 80, 30))
                        text = font.render(f"Level {level_number} Complete!", True, (255, 255, 0))
                        subtitle = font.render("Press any key to continue...", True, (255, 255, 255))
                        window.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 50))
                        window.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, HEIGHT // 2 + 20))

                    pygame.display.update()

    # Handle quit or keypress
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            quit()
                        if event.type == pygame.KEYDOWN:
                            message_run = False

# Move to next level or victory
                if level_number >= 5:
                    sound_manager.play_sound('victory')
                    show_victory(window)
                else:
                    return self.generate_level(window, level_number + 1)


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
# Global generator instance
level_generator = ProceduralLevelGenerator()

def start_procedural_levels(window):
    """Start the procedural level system"""
    level_generator.generate_level(window, 1)
