import pygame
import pygame_gui
from settings import *
from story_generator import StoryGenerator
from voice_generator import VoiceGenerator
import os

class Intro:
    def __init__(self, screen):
        self.screen = screen
        self.manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))
        
        self.background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.background.fill(pygame.Color('#000000'))

        if STORY_GENERATION:
            story_generator = StoryGenerator()
            full_story = story_generator.generate_story()
            self.story_cards = full_story.split('\n\n')  # Split the story into paragraphs
        else:
            self.story_cards = [
                "You wake up in a strange, dark room...",
                "The last thing you remember is boarding a space shuttle...",
                "Now, you must survive and find a way to escape...",
            ]
        self.current_card = 0

        self.text_box = pygame_gui.elements.UITextBox(
            html_text=self.story_cards[self.current_card],
            relative_rect=pygame.Rect((WINDOW_WIDTH//2 - 300, WINDOW_HEIGHT//2 - 100), (600, 200)),
            manager=self.manager
        )

        self.next_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((WINDOW_WIDTH//2 + 200, WINDOW_HEIGHT//2 + 120), (100, 50)),
            text='Next',
            manager=self.manager
        )

        self.voice_generator = VoiceGenerator() if VOICE_GENERATION else None
        self.current_voice_file = None

    def handle_event(self, event):
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.next_button:
                    self.current_card += 1
                    if self.current_card < len(self.story_cards):
                        self.text_box.html_text = self.story_cards[self.current_card]
                        self.text_box.rebuild()
                        if self.voice_generator:
                            self.play_voice()
                    else:
                        return 'intro_finished'
        
        self.manager.process_events(event)
        return None

    def play_voice(self):
        if self.current_voice_file:
            pygame.mixer.music.stop()
            os.remove(self.current_voice_file)
        
        self.current_voice_file = self.voice_generator.generate_voice(
            self.story_cards[self.current_card],
            f"voice_{self.current_card}.mp3"
        )
        pygame.mixer.music.load(self.current_voice_file)
        pygame.mixer.music.play()

    def update(self, time_delta):
        self.manager.update(time_delta)

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.manager.draw_ui(self.screen)
