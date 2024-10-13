import pygame
import pygame_gui
from settings import *
from player import Player
from monster import Monster, RangedMonster, EnhancedMonster
from ui import UI
from save_terminal import SaveTerminal
from npc import NPC
from puzzle import Puzzle
from code_task import CodeTask
from code_terminal import CodeTerminal
from hide import Shelve
from door import Door
import os
import random
from communication_terminal import CommunicationTerminal
from chat_terminal import ChatTerminal, ChatInterface
from music_generator import MusicGenerator
import json

class HidingSpot(pygame.sprite.Sprite):
    def __init__(self, position, size):
        super().__init__()
        self.image = pygame.Surface(size)
        self.image.fill((100, 100, 100))  # Gray color for hiding spots
        self.rect = self.image.get_rect(topleft=position)

class TimerSprite(pygame.sprite.Sprite):
    def __init__(self, duration, position):
        super().__init__()
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        self.font = pygame.font.Font(None, 36)
        self.position = position
        self.image = None
        self.rect = None
        self.update()  # Initialize image and rect

    def update(self):
        remaining_time = self.duration - (pygame.time.get_ticks() - self.start_time) / 1000
        if remaining_time > 0:
            time_text = f"{int(remaining_time)}"
            self.image = self.font.render(time_text, True, (255, 0, 0))
            self.rect = self.image.get_rect(center=self.position)
        else:
            self.kill()

class Level:
    def __init__(self, level_file, terminal_avatar=None):
        self.terminal_avatar = terminal_avatar
        self.screen = pygame.display.get_surface()
        self.visible_sprites = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.monsters = pygame.sprite.Group()
        self.interactables = pygame.sprite.Group()

        # Load level data
        try:
            with open(level_file, 'r') as f:
                self.level_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading level file: {e}")
            self.level_data = {}

        self.background = self.load_background()
        player_pos = self.level_data.get('player_start', {'x': 640, 'y': 670})
        self.player = Player(position=(player_pos['x'], player_pos['y']), groups=[self.visible_sprites])
        self.player.level = self
        print(f"Player initialized at position: {player_pos}")

        self.vertical_zones = []
        self.create_level()
        self.ui = UI(self.player)
        self.events = []

        self.monster_spawn_time = pygame.time.get_ticks() + MONSTER_SPAWN_INTERVAL
        self.monster_warning_time = self.monster_spawn_time - MONSTER_WARNING_DURATION
        self.monster_despawn_time = None
        self.monster = None

        self.puzzle = Puzzle()
        self.code_tasks = [
            {
                "description": "Write a function that adds two numbers",
                "template": "def add(a, b):\n    # Your code here\n    return",
                "correct_solution": "return a + b"
            },
            {
                "description": "Write a function that multiplies two numbers",
                "template": "def multiply(a, b):\n    # Your code here\n    return",
                "correct_solution": "return a * b"
            },
        ]
        self.code_task = CodeTask(self.code_tasks)

        self.load_background_music()
        self.timer_sprite_group = pygame.sprite.Group()
        self.warning_timer_displayed = False

        self.death_image = pygame.image.load('assets/images/death_text.png').convert_alpha()
        self.death_image = pygame.transform.scale(self.death_image, (WINDOW_WIDTH, WINDOW_HEIGHT))
        self.is_game_over = False

        self.communication_terminal = CommunicationTerminal(self.screen)
        self.show_communication_terminal = False

        self.show_chat_interface_flag = False
        self.chat_interface = None

    def create_level(self):
        # Add shelves (hiding spots)
        if 'shelves' in self.level_data and self.level_data['shelves']:
            for shelf_data in self.level_data['shelves']:
                player_width = self.player.rect.width
                player_height = self.player.rect.height
                shelf_width = int(player_width * 1.5)
                shelf_height = int(player_height * 1.2)
                shelf = Shelve((shelf_data['x'], shelf_data['y']), 
                               [self.visible_sprites, self.interactables], 
                               (shelf_width, shelf_height))

        # Add the door
        if 'doors' in self.level_data:
            for door_data in self.level_data['doors']:
                self.door = Door((door_data['x'], door_data['y']), 
                                 [self.visible_sprites, self.interactables], 
                                 self.player, self)

        # Add code terminal
        if 'code_terminal' in self.level_data and self.level_data['code_terminal'] is not None:
            terminal_pos = self.level_data['code_terminal']
            self.code_terminal = CodeTerminal(
                (terminal_pos['x'], terminal_pos['y']),
                [self.visible_sprites, self.interactables],
                avatar=self.terminal_avatar
            )
            self.code_terminal.set_level(self)  # Add this line to set the level
            if hasattr(self, 'door'):
                self.door.set_code_terminal(self.code_terminal)

        # Add vertical zones
        if 'vertical_zones' in self.level_data:
            for zone_data in self.level_data['vertical_zones']:
                zone = pygame.Rect(zone_data['x'], zone_data['y'], zone_data['width'], zone_data['height'])
                self.vertical_zones.append(zone)

        # Add chat terminal
        if 'chat_terminal' in self.level_data and self.level_data['chat_terminal'] is not None:
            chat_terminal_pos = self.level_data['chat_terminal']
            self.chat_terminal = ChatTerminal(
                (chat_terminal_pos['x'], chat_terminal_pos['y']),
                [self.visible_sprites, self.interactables],
                self.screen  # Now self.screen is defined
            )

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.code_task.is_active:
                    self.code_task.hide()
                elif self.show_chat_interface_flag:
                    self.hide_chat_interface()
                else:
                    # Handle pause menu or other actions
                    pass
            elif event.key == KEY_HIDE:
                self.player.toggle_hide()
            elif event.key == KEY_INTERACT:
                self.check_interactables()
            elif event.key == pygame.K_t:
                self.show_communication_terminal = True
            # ... additional key events ...

        if self.show_chat_interface_flag:
            action = self.chat_interface.handle_event(event)
            if action == 'close_chat':
                self.hide_chat_interface()
        elif self.code_task.is_active:
            self.code_task.handle_event(event)

    def update(self, time_delta):
        if self.is_game_over:
            return

        self.visible_sprites.update(time_delta)
        self.monsters.update(time_delta)
        self.timer_sprite_group.update()
        self.player.level = self

        if self.code_task.is_active:
            self.code_task.update(time_delta)
        if self.show_chat_interface_flag:
            self.chat_interface.update(time_delta)

        if not self.code_task.is_active and not self.show_chat_interface_flag:
            # Handle collisions and other game logic
            collided_monsters = pygame.sprite.spritecollide(self.player, self.monsters, False)
            for monster in collided_monsters:
                self.player.take_damage(monster.damage)

            collided_obstacles = pygame.sprite.spritecollide(self.player, self.obstacles, False)
            if collided_obstacles:
                self.player.rect.x -= self.player.velocity.x
                self.player.rect.y -= self.player.velocity.y

            # Monster spawning logic
            current_time = pygame.time.get_ticks()
            if len(self.monsters) == 0 and ENEMIES_ENABLED:
                if current_time >= self.monster_spawn_time:
                    self.spawn_monster()
                elif current_time >= self.monster_warning_time and not self.warning_timer_displayed:
                    warning_duration = (self.monster_spawn_time - current_time) / 1000
                    timer_sprite = TimerSprite(warning_duration, (WINDOW_WIDTH // 2, 50))
                    self.timer_sprite_group.add(timer_sprite)
                    self.warning_timer_displayed = True

        if self.player.health <= 0:
            self.is_game_over = True

        if hasattr(self, 'door') and self.door.is_open and self.player.rect.colliderect(self.door.rect):
            if self.level_data.get('next_level'):
                self.load_next_level(self.level_data['next_level'])

    def draw(self, screen):
        screen.blit(self.background, (0, 0))
        self.visible_sprites.draw(screen)

        for interactable in self.interactables:
            if hasattr(interactable, 'draw_prompt'):
                interactable.draw_prompt(screen, self.player)

        self.ui.draw(screen)

        if self.is_game_over:
            screen.blit(self.death_image, (0, 0))
        if self.code_task.is_active:
            self.code_task.draw(screen)
        if self.show_chat_interface_flag:
            self.chat_interface.draw()
        else:
            self.timer_sprite_group.draw(screen)

    def show_chat_interface(self):
        if not self.chat_interface:
            self.chat_interface = ChatInterface(self.screen)
        self.show_chat_interface_flag = True

    def hide_chat_interface(self):
        self.show_chat_interface_flag = False

    def load_background_music(self):
        pygame.mixer.init()
        if MUSIC_GENERATION:
            music_generator = MusicGenerator()
            music_file = music_generator.generate_music("Eerie space ambient music for a survival horror game")
        else:
            music_file = os.path.join('assets', 'music', 'background_music.ogg')
        
        try:
            if os.path.exists(music_file):
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.play(-1)  # -1 means loop indefinitely
                pygame.mixer.music.set_volume(0.5)  # Set volume to 50%
            else:
                print("Warning: Background music file not found. Continuing without music.")
        except pygame.error as e:
            print(f"Error loading music: {e}")
            print("Continuing without background music.")

    def spawn_monster(self):
        if 'monsters' in self.level_data:
            monster_data = random.choice(self.level_data['monsters'])
            if monster_data['type'] == 'Monster':
                self.monster = Monster((monster_data['x'], monster_data['y']), 
                                       [self.visible_sprites, self.monsters], 
                                       self.player)
            elif monster_data['type'] == 'RangedMonster':
                self.monster = RangedMonster((monster_data['x'], monster_data['y']), 
                                             [self.visible_sprites, self.monsters], 
                                             self.player)
            elif monster_data['type'] == 'EnhancedMonster':
                self.monster = EnhancedMonster((monster_data['x'], monster_data['y']), 
                                               [self.visible_sprites, self.monsters], 
                                               self.player)
            self.monster_spawn_time = pygame.time.get_ticks() + MONSTER_SPAWN_INTERVAL
            self.monster_warning_time = self.monster_spawn_time - MONSTER_WARNING_DURATION
            self.warning_timer_displayed = False

    def restart_level(self):
        self.cleanup()
        self.__init__(self.level_data['current_level'], terminal_avatar=self.terminal_avatar)
        self.is_game_over = False

    def load_background(self):
        background_file = self.level_data.get('background')
        if background_file:
            try:
                background_path = os.path.join('assets', 'images', background_file)
                background = pygame.image.load(background_path).convert()
                background = pygame.transform.scale(background, (WINDOW_WIDTH, WINDOW_HEIGHT))
                print(f"Loaded background image: {background_path}")
                return background
            except pygame.error as e:
                print(f"Error loading background image: {e}")
        else:
            print("No background file specified in level data.")

        # If background loading failed, use a placeholder
        print("Warning: Could not load background image. Using placeholder.")
        background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        background.fill((0, 0, 0))  # Black background
        pygame.draw.rect(background, (50, 50, 50), (100, 100, WINDOW_WIDTH - 200, WINDOW_HEIGHT - 200))
        return background

    def load_next_level(self, next_level_file):
        print(f"Loading next level: {next_level_file}")
        # Clean up current level
        self.cleanup()
        # Reset attributes and load new level data
        self.__init__(next_level_file, terminal_avatar=self.terminal_avatar)
        self.is_game_over = False
        print(f"Level: Loaded next level '{next_level_file}'.")

    def cleanup(self):
        # Stop the music when the level is unloaded
        pygame.mixer.music.stop()

    def check_interactables(self):
        for interactable in self.interactables:
            if pygame.sprite.collide_rect(self.player, interactable):
                print(f"Interacting with {type(interactable).__name__}")
                if isinstance(interactable, Door):
                    interactable.interact()
                elif isinstance(interactable, CodeTerminal):
                    interactable.interact(self)
                elif isinstance(interactable, Shelve):
                    interactable.interact(self.player)
                elif isinstance(interactable, ChatTerminal):
                    interactable.interact(self)
                    self.show_chat_interface()  # Call the method here

    def show_code_task(self):
        self.code_task.show()
        print("Level: Showing code task.")