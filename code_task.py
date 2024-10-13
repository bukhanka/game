import pygame
import pygame_gui
from settings import *

class CodeTask:
    def __init__(self, tasks):
        self.tasks = tasks
        self.current_task_index = 0
        self.is_solved = False
        self.is_active = False

        # GUI elements
        self.manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.background.fill(pygame.Color('#000000'))
        self.setup_gui()

    def setup_gui(self):
        # Task description
        self.description_textbox = pygame_gui.elements.UITextBox(
            html_text="",
            relative_rect=pygame.Rect((50, 50), (WINDOW_WIDTH - 100, 120)),
            manager=self.manager
        )

        # Code editor
        self.code_editor = pygame_gui.elements.UITextEntryBox(
            relative_rect=pygame.Rect((50, 180), (WINDOW_WIDTH - 100, 300)),
            manager=self.manager,
            initial_text=""
        )

        # Submit button
        self.submit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((WINDOW_WIDTH // 2 - 150, 500), (100, 50)),
            text='Submit',
            manager=self.manager
        )

        # Close button
        self.close_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((WINDOW_WIDTH // 2 + 50, 500), (100, 50)),
            text='Close',
            manager=self.manager
        )

        # Feedback text
        self.feedback_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((50, 570), (WINDOW_WIDTH - 100, 30)),
            text='',
            manager=self.manager
        )

        if ADMIN_MODE:
            # Add 'Paste Solution' button
            self.paste_solution_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((WINDOW_WIDTH // 2 - 50, 500), (100, 50)),
                text='Paste Solution',
                manager=self.manager
            )

        # Hide all elements initially
        self.hide_elements()

    def hide_elements(self):
        self.description_textbox.hide()
        self.code_editor.hide()
        self.submit_button.hide()
        self.close_button.hide()
        self.feedback_label.hide()
        if hasattr(self, 'paste_solution_button'):
            self.paste_solution_button.hide()

    def show_elements(self):
        self.description_textbox.show()
        self.code_editor.show()
        self.submit_button.show()
        self.close_button.show()
        self.feedback_label.show()
        if hasattr(self, 'paste_solution_button'):
            self.paste_solution_button.show()

    def handle_event(self, event):
        if not self.is_active:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.hide()
                return

        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.submit_button:
                    self.submit_solution()
                elif event.ui_element == self.close_button:
                    self.hide()
                elif ADMIN_MODE and hasattr(self, 'paste_solution_button') and event.ui_element == self.paste_solution_button:
                    self.paste_solution()

        self.manager.process_events(event)

    def update(self, time_delta):
        if self.is_active:
            self.manager.update(time_delta)

    def draw(self, surface):
        if self.is_active:
            surface.blit(self.background, (0, 0))
            self.manager.draw_ui(surface)

    def submit_solution(self):
        if self.current_task_index < len(self.tasks):
            user_code = self.code_editor.get_text()
            current_task = self.tasks[self.current_task_index]
            
            # Simple check if the code contains the correct solution
            if current_task["correct_solution"] in user_code:
                self.feedback_label.set_text("Task solved! Great job!")
                self.current_task_index += 1
                if self.current_task_index >= len(self.tasks):
                    self.is_solved = True
                    self.feedback_label.set_text("All tasks completed! You can now proceed to the next level.")
                else:
                    self.load_next_task()
            else:
                self.feedback_label.set_text("Incorrect solution. Try again!")

    def load_next_task(self):
        if self.current_task_index < len(self.tasks):
            current_task = self.tasks[self.current_task_index]
            self.description_textbox.set_text(current_task["description"])
            self.code_editor.set_text(current_task["template"])
            self.feedback_label.set_text("")
        else:
            self.description_textbox.set_text("All tasks completed!")
            self.code_editor.set_text("")
            self.feedback_label.set_text("Great job! You've finished all the tasks.")
            self.is_solved = True

    def show(self):
        self.is_active = True
        self.show_elements()
        self.load_next_task()

    def hide(self):
        self.is_active = False
        self.hide_elements()

    def paste_solution(self):
        if ADMIN_MODE and self.current_task_index < len(self.tasks):
            current_task = self.tasks[self.current_task_index]
            self.code_editor.set_text(current_task["template"] + "\n    " + current_task["correct_solution"])
