import pygame

class NPC(pygame.sprite.Sprite):
    def __init__(self, position, groups):
        super().__init__(groups)
        self.image = pygame.Surface((32, 48))
        self.image.fill((0, 255, 0))  # Placeholder for NPC sprite
        self.rect = self.image.get_rect(topleft=position)

    def interact(self):
        # Start conversation or coding tutorial
        pass
