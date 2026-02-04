import pygame
import os

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        
        # Volume settings (0.0 to 1.0) - Keep volumes low
        self.music_volume = 0.2
        self.sfx_volume = 0.3
        
        # Load all sound effects
        self.sounds = {}
        self.load_sounds()
        
        # Background music
        self.current_music = None
        
    def load_sounds(self):
        """Load all sound effects from the assets/game_sounds directory"""
        try:
            # Player sounds
            self.sounds['death'] = pygame.mixer.Sound("assets/game_sounds/Player/death.mp3")
            
            # Gameplay sounds
            self.sounds['coin_collect'] = pygame.mixer.Sound("assets/game_sounds/Gameplay/coin_collect.mp3")
            self.sounds['health_loss'] = pygame.mixer.Sound("assets/game_sounds/Gameplay/health_loss.wav")
            self.sounds['checkpoint'] = pygame.mixer.Sound("assets/game_sounds/Gameplay/checkpoint.mp3")
            self.sounds['fire_activate'] = pygame.mixer.Sound("assets/game_sounds/Gameplay/fire_activate.wav")
            
            
            # UI sounds
           
            self.sounds['level_complete'] = pygame.mixer.Sound("assets/game_sounds/UI/level_completed.mp3")
            self.sounds['victory'] = pygame.mixer.Sound("victory.mp3")
            
            # Set initial volumes
            for sound in self.sounds.values():
                sound.set_volume(self.sfx_volume)
                
            print("✅ All sounds loaded successfully!")
            
        except pygame.error as e:
            print(f"⚠️ Error loading sounds: {e}")
    
    def play_sound(self, sound_name):
        """Play a sound effect"""
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except pygame.error as e:
                print(f"⚠️ Error playing sound {sound_name}: {e}")
        else:
            print(f"⚠️ Sound '{sound_name}' not found")
    
    def play_music(self, music_name, loop=True):
        """Play background music"""
        try:
            music_path = f"assets/game_sounds/Music/{music_name}"
            
            if os.path.exists(music_path):
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(self.music_volume)
                if loop:
                    pygame.mixer.music.play(-1)  # -1 means loop indefinitely
                else:
                    pygame.mixer.music.play()
                self.current_music = music_name
                print(f"🎵 Playing music: {music_name}")
            else:
                print(f"⚠️ Music file not found: {music_path}")
        except pygame.error as e:
            print(f"⚠️ Error playing music {music_name}: {e}")
    
    def stop_music(self):
        """Stop background music"""
        pygame.mixer.music.stop()
        self.current_music = None
    
    def pause_music(self):
        """Pause background music"""
        pygame.mixer.music.pause()
    
    def unpause_music(self):
        """Unpause background music"""
        pygame.mixer.music.unpause()
    
    def set_music_volume(self, volume):
        """Set music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def set_sfx_volume(self, volume):
        """Set sound effects volume (0.0 to 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_volume)
    
    def get_music_volume(self):
        """Get current music volume"""
        return self.music_volume
    
    def get_sfx_volume(self):
        """Get current sound effects volume"""
        return self.sfx_volume
