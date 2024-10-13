import pygame
import pygame_gui
from settings import *

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))
        
        self.background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.background.fill(pygame.Color('#000000'))

        self.start_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 - 50), (200, 50)),
            text='Start Game',
            manager=self.manager
        )

        self.settings_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 + 20), (200, 50)),
            text='Settings',
            manager=self.manager
        )

        self.quit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 + 90), (200, 50)),
            text='Quit',
            manager=self.manager
        )

    def handle_event(self, event):
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.start_button:
                    return 'start_game'
                elif event.ui_element == self.settings_button:
                    return 'show_settings'
                elif event.ui_element == self.quit_button:
                    return 'quit'
        
        self.manager.process_events(event)
        return None

    def update(self, time_delta):
        self.manager.update(time_delta)

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.manager.draw_ui(self.screen)

class SettingsMenu:
    def __init__(self, screen):
        self.screen = screen
        self.manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))
        
        self.background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.background.fill(pygame.Color('#000000'))

        self.enemy_toggle = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 - 50), (200, 50)),
            text='Enemies: ON' if ENEMIES_ENABLED else 'Enemies: OFF',
            manager=self.manager
        )

        self.intro_toggle = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 + 20), (200, 50)),
            text='Intro: ON' if SHOW_INTRO else 'Intro: OFF',
            manager=self.manager
        )

        self.back_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 + 90), (200, 50)),
            text='Back',
            manager=self.manager
        )

    def handle_event(self, event):
        global ENEMIES_ENABLED, SHOW_INTRO
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.enemy_toggle:
                    ENEMIES_ENABLED = not ENEMIES_ENABLED
                    self.enemy_toggle.set_text('Enemies: ON' if ENEMIES_ENABLED else 'Enemies: OFF')
                elif event.ui_element == self.intro_toggle:
                    SHOW_INTRO = not SHOW_INTRO
                    self.intro_toggle.set_text('Intro: ON' if SHOW_INTRO else 'Intro: OFF')
                elif event.ui_element == self.back_button:
                    return 'back_to_main'
        
        self.manager.process_events(event)
        return None

    def update(self, time_delta):
        self.manager.update(time_delta)

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.manager.draw_ui(self.screen)
