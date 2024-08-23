import pygame
import time
from pygame.locals import *

def draw_text_on_screen(text, font_size=72, text_color=(255, 0, 0), display_duration=5):
    # Initialize Pygame
    pygame.init()

    # Get screen dimensions
    screen_width = pygame.display.Info().current_w
    screen_height = pygame.display.Info().current_h

    # Set up display
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME | pygame.SRCALPHA)
    pygame.display.set_caption('Drawing Text')

    # Set up font
    font = pygame.font.SysFont('Arial', font_size, bold=True)

    # Render text
    text_surface = font.render(text, True, text_color)

    # Get text rect and center it
    text_rect = text_surface.get_rect(center=(screen_width // 2, screen_height // 2))

    # Start time
    start_time = time.time()

    # Main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        # Clear the screen
        screen.fill((0, 0, 0, 0))  # Transparent background

        # Draw the text
        screen.blit(text_surface, text_rect)

        # Update the display
        pygame.display.update()

        # Check elapsed time
        if time.time() - start_time > display_duration:
            running = False

    pygame.quit()

if __name__ == "__main__":
    draw_text_on_screen("...")
