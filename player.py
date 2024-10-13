import pygame
from settings import *
import random
import time

class Player(pygame.sprite.Sprite):
    def __init__(self, position, groups):
        super().__init__(groups)
        
        try:
            # Load character sprites
            self.standing_image = pygame.image.load('assets/images/main_char.png').convert_alpha()
            self.moving_spritesheet = pygame.image.load('assets/images/main_char_move.png').convert_alpha()
            self.death_spritesheet = pygame.image.load('assets/images/death.png').convert_alpha()
        except pygame.error as e:
            print(f"Error loading player images: {e}")
            # Create placeholder images
            self.standing_image = pygame.Surface((32, 48))
            self.standing_image.fill((255, 0, 0))  # Red placeholder
            self.moving_spritesheet = pygame.Surface((128, 48))
            self.moving_spritesheet.fill((0, 255, 0))  # Green placeholder
            self.death_spritesheet = pygame.Surface((128, 48))
            self.death_spritesheet.fill((0, 0, 255))  # Blue placeholder
        
        # Scale images to 1/4 of their original size
        scale_factor = 0.375  # This is 0.25 * 1.5, making the sprite 1.5 times bigger than before
        self.standing_image = pygame.transform.scale(self.standing_image, 
                                                     (int(self.standing_image.get_width() * scale_factor), 
                                                      int(self.standing_image.get_height() * scale_factor)))
        self.moving_spritesheet = pygame.transform.scale(self.moving_spritesheet, 
                                                         (int(self.moving_spritesheet.get_width() * scale_factor), 
                                                          int(self.moving_spritesheet.get_height() * scale_factor)))
        self.death_spritesheet = pygame.transform.scale(self.death_spritesheet,
                                                        (int(self.death_spritesheet.get_width() * scale_factor),
                                                         int(self.death_spritesheet.get_height() * scale_factor)))
        
        # Set up animation frames
        self.frame_width = self.moving_spritesheet.get_width() // 4
        self.frame_height = self.moving_spritesheet.get_height()
        self.animation_frames = [
            self.moving_spritesheet.subsurface((i * self.frame_width, 0, self.frame_width, self.frame_height))
            for i in range(4)
        ]
        
        # Set up death animation frames
        self.death_frame_width = self.death_spritesheet.get_width() // 4  # Assuming 4 frames in the death animation
        self.death_frame_height = self.death_spritesheet.get_height()
        self.death_frames = [
            self.death_spritesheet.subsurface((i * self.death_frame_width, 0, self.death_frame_width, self.death_frame_height))
            for i in range(4)
        ]
        
        # Set initial image and rect
        self.image = self.standing_image
        self.rect = self.image.get_rect(center=position)
        
        # Animation variables
        self.facing_right = True
        self.is_moving = False
        self.animation_time = 0
        self.animation_interval = 100  # Change sprite every 100 ms when moving
        self.current_frame = 0
        
        # Death animation variables
        self.is_dying = False
        self.death_animation_time = 0
        self.death_animation_interval = 200  # Change death sprite every 200 ms
        self.current_death_frame = 0

        self.health = PLAYER_HEALTH
        self.stamina = PLAYER_STAMINA
        self.noise_level = 0

        self.velocity = pygame.math.Vector2(0, 0)
        self.is_running = False
        self.is_hidden = False
        self.hiding_spot = None
        self.is_hiding = False
        self.hide_start_time = None
        self.is_qte_active = False
        self.qte_target_key = None
        self.qte_start_time = None
        self.qte_time_limit = 2  # 2 seconds to respond

        self.inventory = []  # List to hold up to 4 items
        self.notes = []  # List to hold collected notes and manuals

        self.level = None  # Will be set after player creation

        self.hiding_cooldown = 0  # Add a cooldown for hiding

        # Keep a copy of the original image for restoring later
        self.original_image = self.image.copy()

    def handle_input(self):
        if not self.is_hiding:
            keys = pygame.key.get_pressed()
            self.velocity = pygame.math.Vector2(0, 0)
            self.is_running = keys[KEY_RUN]
            self.is_moving = False

            if keys[KEY_LEFT]:
                self.velocity.x = -PLAYER_SPEED
                self.facing_right = False
                self.is_moving = True
            elif keys[KEY_RIGHT]:
                self.velocity.x = PLAYER_SPEED
                self.facing_right = True
                self.is_moving = True

            self.velocity.y = 0  # Remove vertical movement

            if self.velocity.magnitude() != 0:
                if self.is_running and self.stamina > 0:
                    self.velocity = self.velocity.normalize() * PLAYER_SPEED * 1.5
                    self.noise_level = min(self.noise_level + 2, 100)
                    self.stamina = max(self.stamina - 1, 0)
                else:
                    self.velocity = self.velocity.normalize() * PLAYER_SPEED
                    self.noise_level = min(self.noise_level + 1, 100)
                    self.stamina = min(self.stamina + 0.5, PLAYER_STAMINA)
            else:
                self.stamina = min(self.stamina + 1, PLAYER_STAMINA)
                self.noise_level = max(self.noise_level - 1, 0)

            # Update hiding cooldown
            if self.hiding_cooldown > 0:
                self.hiding_cooldown -= 1

            if keys[KEY_HIDE]:
                self.toggle_hide()

            # Remove this block since level handles interaction
            # if keys[KEY_INTERACT]:
            #     self.interact()

            if keys[KEY_USE_ITEM]:
                self.use_item()

            if keys[KEY_INVENTORY]:
                self.show_inventory()

            if keys[KEY_NOTES]:
                self.show_notes()
        else:
            self.velocity = pygame.math.Vector2(0, 0)  # Prevent movement
            self.is_moving = False

    def hide(self, hiding_spot):
        if not self.is_hiding and self.hiding_cooldown == 0:
            self.is_hiding = True
            self.hiding_spot = hiding_spot
            self.image.set_alpha(0)  # Make player fully transparent
            self.hide_start_time = pygame.time.get_ticks()
            self.hiding_cooldown = 60  # Cooldown

            # Ensure the alpha value is applied to the image correctly
            self.image = self.image.convert_alpha()

    def unhide(self):
        if self.is_hiding:
            self.is_hiding = False
            self.hiding_spot = None
            self.image.set_alpha(255)  # Make player fully visible
            self.hide_start_time = None
            self.is_qte_active = False
            self.hiding_cooldown = 60  # Cooldown

            # Ensure the alpha value is applied to the image correctly
            self.image = self.image.convert_alpha()

    def toggle_hide(self):
        if self.is_hiding:
            self.unhide()
        else:
            self.check_hiding_spot(self.level.interactables)
            if self.hiding_spot:
                self.hide(self.hiding_spot)
            else:
                print("No hiding spot nearby")

    def update(self, time_delta):
        if self.is_dying:
            self.animate_death()
        else:
            self.handle_input()
            if not self.is_hiding:
                self.image.set_alpha(255)  # Ensure player is visible
                self.rect.x += self.velocity.x
                self.rect.y += self.velocity.y
                self.rect.clamp_ip(pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))
                self.hide_start_time = None
                self.is_qte_active = False
                
                # Update animation
                self.animate()
            else:
                self.velocity = pygame.math.Vector2(0, 0)
                self.is_moving = False
                self.current_frame = 0

    def animate_death(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.death_animation_time > self.death_animation_interval:
            self.death_animation_time = current_time
            self.current_death_frame += 1
            if self.current_death_frame >= len(self.death_frames):
                self.current_death_frame = len(self.death_frames) - 1  # Stay on the last frame
            self.image = self.death_frames[self.current_death_frame]

    def animate(self):
        current_time = pygame.time.get_ticks()
        
        if self.is_moving:
            if current_time - self.animation_time > self.animation_interval:
                self.animation_time = current_time
                self.current_frame = (self.current_frame + 1) % 4
                self.image = self.animation_frames[self.current_frame]
        else:
            self.image = self.standing_image
        
        # Correct the image flipping logic
        if not self.facing_right:
            flipped_image = pygame.transform.flip(self.image, True, False)
            self.image = flipped_image
        # No need to flip when facing right

    def check_monster_proximity(self):
        # Check if any monster is nearby
        for monster in self.level.monsters:
            distance = pygame.math.Vector2(self.rect.center).distance_to(monster.rect.center)
            if distance < monster.check_hiding_spot_radius:
                # Monster is close enough to check the hiding spot
                chance_to_check = 0.005  # Adjust chance as needed
                if random.random() < chance_to_check:
                    self.start_qte()

    def start_qte(self):
        if not self.is_qte_active:
            self.is_qte_active = True
            self.qte_target_key = random.choice(QTE_KEYS)
            self.qte_start_time = pygame.time.get_ticks()
            # Provide visual cue for QTE (e.g., display the target key)
            print(get_text("qte_prompt").format(pygame.key.name(self.qte_target_key)))

    def handle_qte(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.qte_start_time <= self.qte_time_limit * 1000:
            # Wait for player input
            for event in self.level.events:
                if event.type == pygame.KEYDOWN:
                    if event.key == self.qte_target_key:
                        # QTE success
                        self.is_qte_active = False
                        print(get_text("qte_success"))
                        break
                    else:
                        # QTE failed
                        self.is_qte_active = False
                        self.is_hiding = False
                        self.image.fill(WHITE)
                        print(get_text("qte_failure"))
                        break
        else:
            # QTE timed out
            self.is_qte_active = False
            self.is_hiding = False
            self.image.fill(WHITE)
            print(get_text("qte_timeout"))

    def check_hiding_spot(self, hiding_spots):
        # Check if player is colliding with any hiding spots
        for spot in hiding_spots:
            if self.rect.colliderect(spot.rect):
                self.hiding_spot = spot
                return
        self.hiding_spot = None

    def quick_time_event(self):
        if self.is_hidden and random.random() < 0.05:  # 5% chance of triggering QTE when hidden
            target_key = random.choice(QTE_KEYS)
            start_time = time.time()
            
            print(get_text("quick_time_event").format(pygame.key.name(target_key)))

            while time.time() - start_time < 2:  # 2-second window to respond
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == target_key:
                            print("Success!")
                            return True
                        else:
                            print("Failed!")
                            self.is_hidden = False
                            return False
            
            print("Too slow!")
            self.is_hidden = False
            return False

    def add_to_inventory(self, item):
        if len(self.inventory) < 4:
            self.inventory.append(item)
            return True
        return False

    def use_item(self):
        if self.inventory:
            item = self.inventory.pop(0)
            # Implement item use logic here
            print(f"Used item: {item}")

    def take_damage(self, amount):
        if not ADMIN_MODE:
            self.health -= amount
            if self.health <= 0:
                self.die()
        else:
            print(get_text("admin_mode_no_damage"))

    def die(self):
        self.is_dying = True
        self.death_animation_time = pygame.time.get_ticks()
        print(get_text("game_over"))

    def heal(self, amount):
        self.health = min(self.health + amount, PLAYER_HEALTH)

    def show_inventory(self):
        # Implement inventory display logic
        pass

    def show_notes(self):
        # Implement notes display logic
        pass

    def add_note(self, note):
        self.notes.append(note)

    def is_in_vertical_zone(self):
        # Check if the player is within any vertical movement zone
        for zone in self.level.vertical_zones:
            if zone.collidepoint(self.rect.center):
                return True
        return False

    def interact(self):
        # Implement interact logic here
        pass