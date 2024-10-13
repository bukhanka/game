import pygame
from settings import *

class Shelve(pygame.sprite.Sprite):
    def __init__(self, position, groups, size):
        super().__init__(groups)
        
        # Load the sprite sheet
        self.sprite_sheet = pygame.image.load('assets/images/hide.png').convert_alpha()
        
        # Assuming the sprite sheet has 2 frames side by side
        self.frame_width = self.sprite_sheet.get_width() // 2
        self.frame_height = self.sprite_sheet.get_height()
        
        # Create frames
        self.frames = [
            self.sprite_sheet.subsurface((i * self.frame_width, 0, self.frame_width, self.frame_height))
            for i in range(2)
        ]
        
        # Scale frames to the specified size
        self.frames = [pygame.transform.scale(frame, size) for frame in self.frames]
        
        # Set initial image and rect
        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=position)
        
        # Animation variables
        self.current_frame = 0
        self.animation_time = 0
        self.animation_interval = 200  # Change frame every 200 ms
        self.is_animating = False
        
        # Create a font for the interaction prompt
        self.font = pygame.font.Font(None, 24)

    def draw_prompt(self, surface, player):
        if self.rect.colliderect(player.rect.inflate(20, 20)):
            if player.is_hiding and player.hiding_spot == self:
                prompt_text = "Press F to unhide"  # Hiding uses 'F'
            elif not player.is_hiding:
                prompt_text = "Press F to hide"  # Hiding uses 'F'
            else:
                return  # Do not draw prompt if player is hiding in another spot
            
            prompt_surface = self.font.render(prompt_text, True, (255, 255, 255))
            prompt_rect = prompt_surface.get_rect(midbottom=(self.rect.centerx, self.rect.top - 10))
            surface.blit(prompt_surface, prompt_rect)

    def interact(self, player):
        if player.is_hiding and player.hiding_spot == self:
            player.unhide()
        elif not player.is_hiding:
            player.hide(self)
        self.is_animating = True
        self.animation_time = pygame.time.get_ticks()

    def update(self, time_delta):
        if self.is_animating:
            current_time = pygame.time.get_ticks()
            if current_time - self.animation_time > self.animation_interval:
                self.animation_time = current_time
                self.current_frame = (self.current_frame + 1) % 2
                self.image = self.frames[self.current_frame]
                
                if self.current_frame == 0:
                    self.is_animating = False
