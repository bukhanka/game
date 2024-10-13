import pygame
from settings import *

class CodeTerminal(pygame.sprite.Sprite):
    def __init__(self, position, groups, avatar=None):
        super().__init__(groups)
        self.avatar = avatar
        
        if self.avatar:
            self.image = self.avatar
        else:
            self.image = pygame.Surface((32, 48))
            self.image.fill((0, 255, 255))  # Cyan color for code terminal
        
        self.rect = self.image.get_rect(topleft=position)
        
        # Create a font for the interaction prompt
        self.font = pygame.font.Font(None, 24)
        self.prompt_text = self.font.render("Press E to interact", True, (255, 255, 255))
        self.prompt_rect = self.prompt_text.get_rect()
        
        self.code_solved = False
        self.level = None  # Add this line to initialize level
        self.update_prompt_text()  # Update prompt text based on initial code_solved status

    def draw_prompt(self, surface, player):
        if self.rect.colliderect(player.rect.inflate(20, 20)):
            self.prompt_rect.midbottom = (self.rect.centerx, self.rect.top - 10)
            surface.blit(self.prompt_text, self.prompt_rect)

    def interact(self, level):
        print("CodeTerminal: Interacting with code terminal")
        if not self.code_solved:
            level.show_code_task()
            print("CodeTerminal: Showing code task.")
        else:
            print("CodeTerminal: Code task already solved.")
        # Update prompt text based on code_solved status
        self.update_prompt_text()

    def update_prompt_text(self):
        if self.code_solved:
            self.prompt_text = self.font.render("Task already solved!", True, (255, 255, 255))
        else:
            self.prompt_text = self.font.render("Press E to interact", True, (255, 255, 255))

    def update(self, time_delta):
        if self.level and self.level.code_task.is_solved and not self.code_solved:
            self.code_solved = True
            self.update_prompt_text()
            print("CodeTerminal: Code task solved. code_solved set to True.")

    def set_level(self, level):
        self.level = level  # Ensure level is set for access to code_task
