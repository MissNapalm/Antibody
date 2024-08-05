import pygame
import random
import sys
import math
import time

from antibody import Antibody

# Initialize PyGame and mixer
pygame.init()
pygame.mixer.init()

# Load sound effect and music
click_sound = pygame.mixer.Sound('click.wav')  # Replace with your sound file
background_music = 'background_music.mp3'  # Replace with your music file

# Play background music on a loop
pygame.mixer.music.load(background_music)
pygame.mixer.music.play(-1)  # -1 means the music will loop indefinitely

# Set up display
cell_size = 10
grid_width, grid_height = int(cell_size * 78), int(cell_size * 65)  # Increase width by 20%
screen = pygame.display.set_mode((grid_width, grid_height), pygame.RESIZABLE)
pygame.display.set_caption("Germ vs. Antibody Game")

# Set up colors
red = (255, 0, 0)
green_shades = [(0, 255, 0), (0, 200, 0), (34, 139, 34), (50, 205, 50)]  # Different shades of green
white = (255, 255, 255)
black = (0, 0, 0)
gray = (169, 169, 169)
yellow = (255, 255, 0)

# Define cell types
EMPTY = 0
GERM = 1
ANTIBODY = 2

# Create grid
grid_size_x = grid_width // cell_size
grid_size_y = grid_height // cell_size
grid = [[EMPTY for _ in range(grid_size_y)] for _ in range(grid_size_x)]

# Randomly place initial germs
germ_count = 20

while germ_count > 0:
    x, y = random.randint(0, grid_size_x - 1), random.randint(0, grid_size_y - 1)
    if grid[x][y] == EMPTY:
        grid[x][y] = GERM
        germ_count -= 1

# Initialize font
font = pygame.font.SysFont(None, 28)

# Antibody shots management
max_shots = 4
available_shots = max_shots
last_shot_time = time.time()
recharge_delay = 2  # Delay before starting to recharge after reaching zero
recharge_time_remaining = recharge_delay
recharging = False

# Fullscreen flag
is_fullscreen = False

# Capsule data
capsule_position = None
capsule_creation_time = None
capsule_duration = 3  # 3 seconds before explosion

def draw_background():
    # Draw a red rectangle as the background, matching the grid size
    background_rect = pygame.Rect(0, 0, grid_width, grid_height)
    pygame.draw.rect(screen, red, background_rect)

def draw_grid(antibodies):
    for x in range(grid_size_x):
        for y in range(grid_size_y):
            if grid[x][y] == GERM:
                color = random.choice(green_shades)  # Random shade of green for germs
                pygame.draw.rect(screen, color, pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size))
    # Draw antibodies
    for antibody in antibodies:
        antibody.draw(screen, cell_size)

def calculate_infection_level():
    germ_count = sum(row.count(GERM) for row in grid)
    total_cells = grid_size_x * grid_size_y
    infection_level = (germ_count / total_cells) * 100
    return infection_level

def draw_infection_level():
    infection_level = calculate_infection_level()
    text = font.render(f"Infection Level: {infection_level:.1f}%", True, white)
    screen.blit(text, (10, 10))
    return infection_level

def draw_shots_available():
    if recharging:
        text = font.render(f"Shots recharging, wait {recharge_time_remaining:.1f} secs", True, white)
    else:
        text = font.render(f"Antibody Shots: {available_shots}", True, white)
    screen.blit(text, (10, 50))

def draw_wave_info(wave_number, screen_width, screen_height):
    text = font.render(f"Prepare for the Next Wave...", True, white)
    screen.blit(text, (screen_width // 2 - text.get_width() // 2, screen_height // 2 - text.get_height() // 2))

def draw_game_over(message, screen_width, screen_height):
    text = font.render(message, True, white)
    screen.fill(black)  # Clear the screen with black
    screen.blit(text, (screen_width // 2 - text.get_width() // 2, screen_height // 2 - text.get_height() // 2))
    pygame.display.flip()
    time.sleep(2)  # Display the message for 2 seconds
    pygame.quit()
    sys.exit()

def sprout(aggression_rate):
    new_germs = []

    # Spread germs based on aggression rate
    for x in range(grid_size_x):
        for y in range(grid_size_y):
            if grid[x][y] == GERM:
                if random.random() < aggression_rate:  # Variable aggressive spread
                    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
                    random.shuffle(directions)
                    for dx, dy in directions:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < grid_size_x and 0 <= ny < grid_size_y and grid[nx][ny] == EMPTY:
                            new_germs.append((nx, ny))
                            break

    for nx, ny in new_germs:
        grid[nx][ny] = GERM

def toggle_fullscreen():
    global is_fullscreen, screen
    if is_fullscreen:
        screen = pygame.display.set_mode((grid_width, grid_height))
        pygame.display.set_caption("Germ vs. Antibody Game")
        is_fullscreen = False
    else:
        screen = pygame.display.set_mode((grid_width, grid_height), pygame.FULLSCREEN)
        pygame.display.set_caption("Germ vs. Antibody Game - Fullscreen")
        is_fullscreen = True

def draw_capsule():
    if capsule_position is not None:
        x, y = capsule_position
        pygame.draw.rect(screen, yellow, pygame.Rect(x * cell_size - 32.5, y * cell_size - 32.5, 65, 65))

def check_capsule_explosion():
    global capsule_position, capsule_creation_time
    if capsule_position and time.time() - capsule_creation_time >= capsule_duration:
        x, y = capsule_position
        destroy_radius(x, y, 100)  # Destroy in a 100px radius
        capsule_position = None  # Remove capsule after explosion

def destroy_radius(x, y, radius):
    # Destroy germs and antibodies in a circular radius
    for i in range(max(0, x - radius // cell_size), min(grid_size_x, x + radius // cell_size + 1)):
        for j in range(max(0, y - radius // cell_size), min(grid_size_y, y + radius // cell_size + 1)):
            if math.sqrt((x - i) ** 2 + (y - j) ** 2) * cell_size <= radius:
                if grid[i][j] == GERM or grid[i][j] == ANTIBODY:
                    grid[i][j] = EMPTY

# Main game loop
running = True
clock = pygame.time.Clock()

# List to store antibodies
antibodies = []

wave_number = 1
game_over = False
aggression_rate = 0.03  # Initial aggression rate for germ spread

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:  # Press 'F' to toggle fullscreen
                toggle_fullscreen()
            if event.key == pygame.K_y:  # Press 'Y' to create capsule in the center
                capsule_position = (grid_size_x // 2, grid_size_y // 2)
                capsule_creation_time = time.time()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left-click
                # Create an antibody at the click position, if within bounds and cell is empty
                x, y = event.pos[0] // cell_size, event.pos[1] // cell_size
                if 0 <= x < grid_size_x and 0 <= y < grid_size_y:
                    if grid[x][y] == EMPTY and available_shots > 0:
                        antibodies.append(Antibody(x, y))  # Start the initial antibody at the click position
                        available_shots -= 1
                        if available_shots == 0:
                            last_shot_time = time.time()
                            recharging = True
                        # Play the click sound effect
                        click_sound.play()
            elif event.button == 3:  # Right-click to start recharge sequence
                if available_shots < max_shots:
                    last_shot_time = time.time()
                    recharging = True

    # Handle recharging logic
    if recharging:
        current_time = time.time()
        recharge_time_remaining = recharge_delay - (current_time - last_shot_time)
        if recharge_time_remaining <= 0:
            available_shots = max_shots
            recharging = False

    # Update all antibodies
    for antibody in antibodies[:]:
        antibody.update(grid, grid_size_x, grid_size_y)
        if not antibody.active:
            antibodies.remove(antibody)

    sprout(aggression_rate)

    screen.fill(black)  # Fill the background with black
    draw_background()  # Draw the red rectangle background
    draw_grid(antibodies)
    draw_capsule()  # Draw capsule if it exists
    check_capsule_explosion()  # Check for capsule explosion
    infection_level = draw_infection_level()  # Draw infection level text
    draw_shots_available()  # Draw available shots

    if infection_level == 0.0 and not game_over:
        screen_width, screen_height = screen.get_size()  # Use actual screen size
        draw_wave_info(wave_number, screen_width, screen_height)
        pygame.display.flip()
        time.sleep(3)  # Pause for 3 seconds
        grid = [[EMPTY for _ in range(grid_size_y)] for _ in range(grid_size_x)]
        germ_count = wave_number * 20  # Increase germs based on wave number

        for _ in range(germ_count):
            x, y = random.randint(0, grid_size_x - 1), random.randint(0, grid_size_y - 1)
            if grid[x][y] == EMPTY:
                grid[x][y] = GERM

        wave_number += 1
        aggression_rate += 0.005  # Increase aggression with each wave
        game_over = False  # Reset game over flag for new wave

    if infection_level >= 100.0:
        screen_width, screen_height = screen.get_size()  # Use actual screen size
        draw_game_over("Game Over, You Lose!", screen_width, screen_height)
        game_over = True

    # Draw wave number in the top left corner
    wave_text = font.render(f"Wave: {wave_number}", True, white)
    screen.blit(wave_text, (10, 90))

    pygame.display.flip()
    clock.tick(26)  # Set FPS to 26 for a smoother game

pygame.quit()
sys.exit()
