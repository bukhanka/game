import pygame
import pygame_gui
from settings import *
from level import Level
from menu import MainMenu, SettingsMenu
from intro import Intro
import sys
import traceback  # Add this import
from player import Player

def main():
    try:
        pygame.init()
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Space Survival Horror")
        clock = pygame.time.Clock()
        
        main_menu = MainMenu(screen)
        settings_menu = SettingsMenu(screen)
        current_screen = 'main_menu'
        
        try:
            terminal_avatar = pygame.image.load('assets/images/terminal.png')
            terminal_avatar = pygame.transform.scale(terminal_avatar, (50, 50))
        except pygame.error:
            print("Warning: Could not load terminal avatar. Using default.")
            terminal_avatar = pygame.Surface((50, 50))
            terminal_avatar.fill((0, 255, 0))  # Green placeholder
        
        level = None
        intro = Intro(screen)

        running = True
        while running:
            time_delta = clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if current_screen == 'main_menu':
                    action = main_menu.handle_event(event)
                    if action == 'start_game':
                        if SHOW_INTRO:
                            current_screen = 'intro'
                        else:
                            current_screen = 'game'
                            level = Level('assets/levels/level1.json', terminal_avatar=terminal_avatar)
                    elif action == 'show_settings':
                        current_screen = 'settings'
                    elif action == 'quit':
                        running = False
                elif current_screen == 'settings':
                    action = settings_menu.handle_event(event)
                    if action == 'back_to_main':
                        current_screen = 'main_menu'
                elif current_screen == 'intro':
                    action = intro.handle_event(event)
                    if action == 'intro_finished':
                        current_screen = 'game'
                        level = Level('assets/levels/level1.json', terminal_avatar=terminal_avatar)
                elif current_screen == 'game':
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            level.code_task.hide()
                        elif event.key == pygame.K_f:
                            print("F key pressed")
                        elif event.key == pygame.K_e and level and level.is_game_over:
                            level.restart_level()
                            print("Player respawned")
                    level.handle_event(event)

            if current_screen == 'main_menu':
                main_menu.update(time_delta)
                main_menu.draw()
            elif current_screen == 'settings':
                settings_menu.update(time_delta)
                settings_menu.draw()
            elif current_screen == 'intro':
                intro.update(time_delta)
                intro.draw()
            elif current_screen == 'game':
                level.update(time_delta)
                screen.fill((0, 0, 0))
                level.draw(screen)

            # Add respawn prompt if game is over
            if level and level.is_game_over:
                font = pygame.font.Font(None, 36)
                respawn_text = font.render("Press E to respawn", True, (255, 255, 255))
                screen.blit(respawn_text, (WINDOW_WIDTH // 2 - respawn_text.get_width() // 2, WINDOW_HEIGHT - 50))

            pygame.display.flip()

        if level:
            level.cleanup()
    except pygame.error as e:
        print(f"Pygame error: {e}")
        traceback.print_exc()  # Add this line
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        traceback.print_exc()  # Add this line
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
