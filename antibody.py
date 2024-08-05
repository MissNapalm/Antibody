import random
import time
import pygame

class Antibody:
    fade_duration = 2  # Total duration the antibodies should exist

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.creation_time = time.time()
        self.cells = [(x, y)]  # Start with a single cell
        self.active = True
        self.alpha = 255  # Start fully opaque
        self.fade_out_start_time = self.fade_duration - 0.5  # Fade out begins in the last 0.5 seconds

    def update(self, grid, grid_size_x, grid_size_y):
        if not self.active:
            return

        elapsed_time = time.time() - self.creation_time

        # Spread if still active
        if elapsed_time < self.fade_duration:
            new_cells = []
            for (x, y) in self.cells:
                directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
                random.shuffle(directions)
                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < grid_size_x and 0 <= ny < grid_size_y:
                        if grid[nx][ny] == 0 or grid[nx][ny] == 1:  # Empty or Germ
                            if random.random() < 0.2:  # Spread probability
                                new_cells.append((nx, ny))
                                grid[nx][ny] = 2  # Convert to ANTIBODY (and remove germ if present)

            self.cells.extend(new_cells)

        # Check if the antibody should fade out
        if elapsed_time >= self.fade_duration:
            self.active = False
            self.clear(grid)

        # Update alpha value for fade-out effect, only in the last 0.5 seconds
        if elapsed_time > self.fade_out_start_time:
            fade_elapsed = elapsed_time - self.fade_out_start_time
            fade_total_duration = self.fade_duration - self.fade_out_start_time
            self.alpha = max(0, int(255 * (1 - fade_elapsed / fade_total_duration)))

    def clear(self, grid):
        for (x, y) in self.cells:
            grid[x][y] = 0  # Set to EMPTY

    def draw(self, screen, cell_size, offset_x=0):
        for (x, y) in self.cells:
            # Create a surface for the antibody with alpha transparency
            antibody_surface = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
            antibody_surface.fill((255, 255, 255, self.alpha))
            screen.blit(antibody_surface, (x * cell_size + offset_x, y * cell_size))
