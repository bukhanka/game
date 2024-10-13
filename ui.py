import pygame
from settings import *

class UI:
    def __init__(self, player):
        self.player = player
        self.font = pygame.font.Font(None, 36)

    def draw(self, screen):
        # Draw health bar
        health_text = self.font.render(f"{get_text('health')}: {self.player.health}", True, WHITE)
        pygame.draw.rect(screen, WHITE, (10, 10, 100, 20), 0)
        pygame.draw.rect(screen, BLACK, (10, 10, 100 * (self.player.health / PLAYER_HEALTH), 20), 0)
        screen.blit(health_text, (120, 10))

        # Draw stamina bar
        stamina_text = self.font.render(f"{get_text('stamina')}: {int(self.player.stamina)}", True, LIGHT_BLUE)
        pygame.draw.rect(screen, LIGHT_BLUE, (10, 40, 100, 20), 0)
        pygame.draw.rect(screen, BLACK, (10, 40, 100 * (self.player.stamina / PLAYER_STAMINA), 20), 0)
        screen.blit(stamina_text, (120, 40))

        # Draw noise level
        noise_color = (255, 255 - self.player.noise_level * 2.55, 255 - self.player.noise_level * 2.55)
        noise_text = self.font.render(f"{get_text('noise')}: {self.player.noise_level}", True, noise_color)
        screen.blit(noise_text, (10, 70))

        # Draw inventory slots
        for i in range(4):
            pygame.draw.rect(screen, WHITE, (WINDOW_WIDTH - 110 + i * 25, WINDOW_HEIGHT - 40, 20, 20), 1)
            if i < len(self.player.inventory):
                pygame.draw.rect(screen, WHITE, (WINDOW_WIDTH - 108 + i * 25, WINDOW_HEIGHT - 38, 16, 16), 0)

        # Draw notes icon
        pygame.draw.rect(screen, WHITE, (10, WINDOW_HEIGHT - 40, 20, 20), 1)
        if self.player.notes:
            pygame.draw.rect(screen, WHITE, (12, WINDOW_HEIGHT - 38, 16, 16), 0)
