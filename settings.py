import pygame
import json

# Admin mode settings
ADMIN_MODE = True  # Set this to True to enable admin mode
ENEMIES_ENABLED = True  # Set this to False to disable enemies
SHOW_INTRO = False   # Set this to False to skip the intro

# AI mode settings
AI_MODE = False  # Set this to True to enable AI mode
STORY_GENERATION = False  # Set this to True to enable story generation
MUSIC_GENERATION = False  # Set this to True to enable music generation
VOICE_GENERATION = False  # Set this to True to enable voice generation

# Window settings
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60

# Player settings
PLAYER_SPEED = 5
PLAYER_HEALTH = 5
PLAYER_STAMINA = 100

# Monster settings
MONSTER_SPEED = 3
MONSTER_DETECTION_RADIUS = 200
MONSTER_NOISE_THRESHOLD = 50
MONSTER_SPAWN_INTERVAL = 20000  # 20 seconds in milliseconds
MONSTER_STAY_DURATION = 30000   # 30 seconds in milliseconds
MONSTER_WARNING_DURATION = 10000  # 10 seconds in milliseconds

# Colors
WHITE = (255, 255, 255)
LIGHT_BLUE = (173, 216, 230)
BLACK = (0, 0, 0)

# Control keys
KEY_LEFT = pygame.K_a
KEY_RIGHT = pygame.K_d
KEY_UP = pygame.K_w
KEY_DOWN = pygame.K_s
KEY_HIDE = pygame.K_f          # Changed from KEY_INTERACT to KEY_HIDE
KEY_INTERACT = pygame.K_e      # Changed from KEY_USE_ITEM to KEY_INTERACT
KEY_USE_ITEM = pygame.K_x      # Assign a new key for using items if needed
KEY_INVENTORY = pygame.K_c
KEY_NOTES = pygame.K_q
KEY_RUN = pygame.K_LSHIFT

# Quick Time Event keys
QTE_KEYS = [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_q, pygame.K_e]

# Load language data
with open('localization.json', 'r', encoding='utf-8') as f:
    LANG_DATA = json.load(f)

# Set default language (can be changed in-game)
CURRENT_LANG = 'en'

def get_text(key):
    return LANG_DATA[CURRENT_LANG].get(key, key)

# Chat terminal settings
CHAT_TERMINAL_IMAGE = 'assets/images/chat_terminal.png'
