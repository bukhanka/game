import pygame
import pygame_gui
from settings import *

class CommunicationTerminal:
    def __init__(self, screen):
        self.screen = screen
        self.manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))
        
        self.background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.background.fill(pygame.Color('#000000'))

        self.text_box = pygame_gui.elements.UITextBox(
            html_text="Welcome to the Communication Terminal. Here you can learn about the ship's history and current situation.",
            relative_rect=pygame.Rect((50, 50), (WINDOW_WIDTH - 100, WINDOW_HEIGHT - 200)),
            manager=self.manager
        )

        self.close_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((WINDOW_WIDTH//2 - 50, WINDOW_HEIGHT - 100), (100, 50)),
            text='Close',
            manager=self.manager
        )

    def handle_event(self, event):
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.close_button:
                    return 'close_terminal'
        
        self.manager.process_events(event)
        return None

    def update(self, time_delta):
        self.manager.update(time_delta)

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.manager.draw_ui(self.screen)
