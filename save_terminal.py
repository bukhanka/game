import pygame

class SaveTerminal(pygame.sprite.Sprite):
    def __init__(self, position, groups):
        super().__init__(groups)
        self.image = pygame.Surface((32, 48))
        self.image.fill((0, 0, 255))  # Placeholder for terminal sprite
        self.rect = self.image.get_rect(topleft=position)

    def interact(self):
        # Save game state
        pass
