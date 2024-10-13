import pygame
from settings import *
import math
import random

class Monster(pygame.sprite.Sprite):
    def __init__(self, position, groups, player):
        super().__init__(groups)
        
        try:
            # Load sprite sheets
            self.movement_spritesheet = pygame.image.load('assets/images/enemy.png').convert_alpha()
            self.attack_spritesheet = pygame.image.load('assets/images/enemy_attack.png').convert_alpha()
        except pygame.error as e:
            print(f"Error loading monster images: {e}")
            # Create placeholder images
            self.movement_spritesheet = pygame.Surface((96, 32))
            self.movement_spritesheet.fill((255, 0, 0))  # Red placeholder
            self.attack_spritesheet = pygame.Surface((160, 32))
            self.attack_spritesheet.fill((255, 255, 0))  # Yellow placeholder
        
        # Set up animation frames
        self.movement_frames = self.get_frames(self.movement_spritesheet, 3)
        self.attack_frames = self.get_frames(self.attack_spritesheet, 5)
        
        # Scale frames to be 1.5 times bigger than the player
        player_width = player.rect.width
        player_height = player.rect.height
        monster_width = int(player_width * 1.5)
        monster_height = int(player_height * 1.5)
        
        self.movement_frames = [pygame.transform.scale(frame, (monster_width, monster_height)) for frame in self.movement_frames]
        self.attack_frames = [pygame.transform.scale(frame, (monster_width, monster_height)) for frame in self.attack_frames]
        
        self.image = self.movement_frames[0]
        self.rect = self.image.get_rect(topleft=position)

        self.speed = MONSTER_SPEED
        self.detect_radius = MONSTER_DETECTION_RADIUS
        self.player = player
        self.damage = 1
        self.state = 'patrol'

        self.gravity = 0.8
        self.velocity = pygame.math.Vector2(0, 0)

        self.check_hiding_spot_radius = 100  # Radius within which the monster can check hiding spots
        self.checking_hiding_spot = False

        # Animation variables
        self.current_frame = 0
        self.animation_time = 0
        self.animation_interval = 200  # Change sprite every 200 ms
        self.is_attacking = False
        self.attack_cooldown = 0
        self.attack_duration = 1000  # 1 second for full attack animation

        self.direction = random.choice([-1, 1])  # Start with a random direction
        self.direction_change_time = pygame.time.get_ticks() + random.randint(3000, 5000)  # Change direction every 3-5 seconds
        self.spawn_time = pygame.time.get_ticks()
        self.initial_y = self.rect.y
        self.y_offset = 20  # Adjust this value to move the monster lower

    def get_frames(self, spritesheet, num_frames):
        frame_width = spritesheet.get_width() // num_frames
        frame_height = spritesheet.get_height()
        return [spritesheet.subsurface((i * frame_width, 0, frame_width, frame_height)) for i in range(num_frames)]

    def update(self, time_delta):
        current_time = pygame.time.get_ticks()

        # Change direction periodically
        if current_time > self.direction_change_time:
            self.direction *= -1  # Reverse direction
            self.direction_change_time = current_time + random.randint(3000, 5000)

        # Move in the current direction
        self.rect.x += self.speed * self.direction * time_delta  # Use time_delta for smooth movement
        self.rect.y = self.initial_y + self.y_offset  # Keep the monster slightly lower

        # Keep the monster within the screen bounds
        if self.rect.left < 0:
            self.rect.left = 0
            self.direction = 1
        elif self.rect.right > WINDOW_WIDTH:
            self.rect.right = WINDOW_WIDTH
            self.direction = -1

        # Update animation
        self.animate(time_delta)  # Pass time_delta to animate method

        # Despawn after 10 seconds
        if current_time - self.spawn_time > 10000:  # 10 seconds
            self.kill()

    def animate(self, time_delta):
        self.animation_time += time_delta * 1000  # Convert to milliseconds
        
        if self.animation_time > self.animation_interval:
            self.animation_time = 0
            
            if self.is_attacking:
                self.current_frame = (self.current_frame + 1) % len(self.attack_frames)
                self.image = self.attack_frames[self.current_frame]
                
                if self.current_frame == 0:
                    self.is_attacking = False
            else:
                self.current_frame = (self.current_frame + 1) % len(self.movement_frames)
                self.image = self.movement_frames[self.current_frame]

        # Flip the image based on direction
        if self.direction > 0:
            self.image = pygame.transform.flip(self.image, True, False)

    def start_attack(self):
        self.is_attacking = True
        self.current_frame = 0
        self.attack_cooldown = self.attack_duration

    def is_in_vertical_zone(self):
        # Check if the monster is within any vertical movement zone
        if hasattr(self.player.level, 'vertical_zones'):
            for zone in self.player.level.vertical_zones:
                if zone.collidepoint(self.rect.center):
                    return True
        return False

    def player_discovered(self):
        self.state = 'chase'
        self.speed *= 1.5  # Increase speed when player is discovered

    def can_see_player(self):
        # Implement line-of-sight check here
        # For simplicity, we'll just check if the player is not hiding
        return not self.player.is_hiding

class RangedMonster(Monster):
    def __init__(self, position, groups, player):
        super().__init__(position, groups, player)
        # Load ranged monster specific sprite sheets here if available
        # For now, we'll just tint the existing sprites green
        self.movement_frames = [self.tint_surface(frame, (0, 255, 0)) for frame in self.movement_frames]
        self.attack_frames = [self.tint_surface(frame, (0, 255, 0)) for frame in self.attack_frames]
        self.image = self.movement_frames[0]
        self.speed = MONSTER_SPEED * 1.2
        self.attack_range = 200

    def tint_surface(self, surface, tint_color):
        tinted_surface = surface.copy()
        tinted_surface.fill(tint_color, special_flags=pygame.BLEND_RGB_MULT)
        return tinted_surface

    def update(self, time_delta):
        super().update(time_delta)
        distance = pygame.math.Vector2(self.player.rect.center) - pygame.math.Vector2(self.rect.center)
        if self.attack_range > distance.length() > 100:
            # Attack logic here (e.g., spawn a projectile)
            pass
        elif distance.length() <= 100:
            # Move away from player
            if distance.length() != 0:
                direction = distance.normalize()
                self.velocity.x = -direction.x * self.speed * time_delta  # Use time_delta for smooth movement

class EnhancedMonster(Monster):
    def __init__(self, position, groups, player):
        super().__init__(position, groups, player)
        # Load enhanced monster specific sprite sheets here if available
        # For now, we'll just tint the existing sprites blue
        self.movement_frames = [self.tint_surface(frame, (0, 0, 255)) for frame in self.movement_frames]
        self.attack_frames = [self.tint_surface(frame, (0, 0, 255)) for frame in self.attack_frames]
        self.image = self.movement_frames[0]
        self.speed = MONSTER_SPEED * 0.8
        self.damage = 2
        self.detect_radius = MONSTER_DETECTION_RADIUS * 1.5

    def tint_surface(self, surface, tint_color):
        tinted_surface = surface.copy()
        tinted_surface.fill(tint_color, special_flags=pygame.BLEND_RGB_MULT)
        return tinted_surface
