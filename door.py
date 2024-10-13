import pygame
from settings import *

class Door(pygame.sprite.Sprite):
    def __init__(self, position, groups, player, level):
        super().__init__(groups)
        
        try:
            # Load the sprite sheet
            self.sprite_sheet = pygame.image.load('assets/images/door.png').convert_alpha()
        except pygame.error as e:
            print(f"Error loading door image: {e}")
            # Create a placeholder image
            self.sprite_sheet = pygame.Surface((96, 128))  # Adjust size as needed
            self.sprite_sheet.fill((200, 200, 200))  # Gray color for placeholder
        
        # Assuming the sprite sheet has 3 frames side by side, but we'll only use the first 2
        self.frame_width = self.sprite_sheet.get_width() // 3
        self.frame_height = self.sprite_sheet.get_height()
        
        # Create frames using only the first two sprites
        self.frames = [
            self.sprite_sheet.subsurface((i * self.frame_width, 0, self.frame_width, self.frame_height))
            for i in range(2)
        ]
        
        # Scale frames to be 3 times wider and 4 times taller than the player
        player_width = player.rect.width
        player_height = player.rect.height
        door_width = int(player_width * 3)
        door_height = int(player_height * 4)
        self.frames = [pygame.transform.scale(frame, (door_width, door_height)) for frame in self.frames]
        
        # Set initial image and rect
        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=position)
        
        # Animation variables
        self.current_frame = 0
        self.animation_time = 0
        self.animation_interval = 200
        self.is_animating = False
        self.is_open = False
        
        # Create a font for the interaction prompt
        self.font = pygame.font.Font(None, 24)
        self.prompt_text = self.font.render("Press F to open/close", True, (255, 255, 255))
        self.prompt_rect = self.prompt_text.get_rect()
        
        self.level = level
        self.code_terminal = None

    def set_code_terminal(self, code_terminal):
        self.code_terminal = code_terminal

    def draw_prompt(self, surface, player):
        if self.rect.colliderect(player.rect.inflate(20, 20)):
            if not self.code_terminal:
                prompt_text = "Press E to enter"
            elif self.code_terminal and self.code_terminal.code_solved:
                prompt_text = "Press E to enter save room"
            else:
                prompt_text = "Solve the code task to unlock"
            self.prompt_text = self.font.render(prompt_text, True, (255, 255, 255))
            self.prompt_rect.midbottom = (self.rect.centerx, self.rect.top - 10)
            surface.blit(self.prompt_text, self.prompt_rect)

    def interact(self):
        print(f"Door: Interacting. Code terminal exists: {self.code_terminal is not None}")
        if self.code_terminal:
            print(f"Door: Code solved status: {self.code_terminal.code_solved}")

        if not self.code_terminal or (self.code_terminal and self.code_terminal.code_solved):
            print("Door: Door will open.")
            self.is_animating = True
            self.animation_time = pygame.time.get_ticks()
            self.is_open = True
            # The actual level transition is handled in the Level class
        else:
            print("Door: Code not solved, door remains locked.")
            self.prompt_text = self.font.render("Solve the code task to unlock", True, (255, 255, 255))

    def update(self, time_delta):
        if self.is_animating:
            current_time = pygame.time.get_ticks()
            if current_time - self.animation_time > self.animation_interval:
                self.animation_time = current_time
                self.current_frame = min(self.current_frame + 1, 1)
                self.image = self.frames[self.current_frame]
                
                if self.current_frame == 1:
                    self.is_animating = False
