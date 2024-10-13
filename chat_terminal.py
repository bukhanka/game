import pygame
import pygame_gui
from settings import *
from openai import OpenAI
import os

class ChatTerminal(pygame.sprite.Sprite):
    def __init__(self, position, groups, screen):
        super().__init__(groups)
        try:
            self.image = pygame.image.load(CHAT_TERMINAL_IMAGE).convert_alpha()
            self.image = pygame.transform.scale(self.image, (50, 50))  # Adjust size as needed
        except pygame.error:
            print(f"Warning: Could not load chat terminal image: {CHAT_TERMINAL_IMAGE}")
            self.image = pygame.Surface((50, 50))
            self.image.fill((0, 255, 255))  # Cyan color as a placeholder
        self.rect = self.image.get_rect(topleft=position)
        
        self.font = pygame.font.Font(None, 24)
        self.prompt_text = self.font.render("Press F to chat", True, (255, 255, 255))
        self.prompt_rect = self.prompt_text.get_rect()
        
        self.screen = screen
        self.chat_interface = ChatInterface(self.screen)
        self.chat_active = False

    def draw_prompt(self, surface, player):
        if self.rect.colliderect(player.rect.inflate(20, 20)):
            self.prompt_rect.midbottom = (self.rect.centerx, self.rect.top - 10)
            surface.blit(self.prompt_text, self.prompt_rect)

    def interact(self, level):
        print("ChatTerminal: Opening chat interface")
        level.show_chat_interface()  # This now calls the method in Level

    def handle_event(self, event):
        if self.chat_active:
            action = self.chat_interface.handle_event(event)
            if action == 'close_chat':
                self.chat_active = False
            return True
        return False

    def update(self, time_delta=0):  # Add a default value for time_delta
        if self.chat_active:
            self.chat_interface.update(time_delta)

    def draw(self):
        if self.chat_active:
            self.chat_interface.draw()

class ChatInterface:
    def __init__(self, screen):
        self.screen = screen
        self.manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))
        
        self.background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.background.fill(pygame.Color('#000000'))

        self.chat_history = pygame_gui.elements.UITextBox(
            html_text="",
            relative_rect=pygame.Rect((50, 50), (WINDOW_WIDTH - 100, WINDOW_HEIGHT - 200)),
            manager=self.manager
        )

        self.input_field = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((50, WINDOW_HEIGHT - 100), (WINDOW_WIDTH - 200, 50)),
            manager=self.manager
        )

        self.send_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((WINDOW_WIDTH - 120, WINDOW_HEIGHT - 100), (70, 50)),
            text='Send',
            manager=self.manager
        )

        self.close_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((WINDOW_WIDTH - 120, 20), (100, 30)),
            text='Close',
            manager=self.manager
        )

        try:
            self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        except Exception as e:
            print(f"Warning: Error initializing OpenAI client: {e}")
            self.client = None

        self.conversation_history = []

    def handle_event(self, event):
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.send_button:
                    self.send_message()
                elif event.ui_element == self.close_button:
                    return 'close_chat'
        
        self.manager.process_events(event)
        return None

    def send_message(self):
        message = self.input_field.get_text()
        if message:
            self.chat_history.html_text += f"<br><b>You:</b> {message}"
            self.chat_history.rebuild()
            self.input_field.set_text("")
            
            # Here you would integrate with your AI model to generate a response
            ai_response = self.get_ai_response(message)
            self.chat_history.html_text += f"<br><b>AI:</b> {ai_response}"
            self.chat_history.rebuild()

    def get_ai_response(self, message):
        self.conversation_history.append({"role": "user", "content": message})
        
        if not self.client:
            return "AI is currently unavailable. Please try again later."

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI assistant in a space survival horror game. Provide information and guidance to the player."},
                    *self.conversation_history
                ]
            )

            ai_response = response.choices[0].message.content
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            return ai_response
        except Exception as e:
            print(f"Error getting AI response: {e}")
            return "Sorry, I couldn't process your request. Please try again."

    def update(self, time_delta):
        self.manager.update(time_delta)

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.manager.draw_ui(self.screen)
