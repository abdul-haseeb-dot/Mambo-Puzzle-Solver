import pygame
import sys
from enum import Enum, auto
from tile import Tile
from button import Button
from connector import Connector
from solver import solve_mambo


class ScreenState(Enum):
    MENU = auto()
    DESIGN = auto()
    SOLVE = auto()


def create_grid(grid_size, window_width):
    grid = []
    connectors = []

    AVAILABLE_SPACE = 440
    GAP = 8
    TOP_MARGIN = 150

    tile_size = (AVAILABLE_SPACE - (GAP * (grid_size - 1))) // grid_size
    total_grid_width = (grid_size * tile_size) + ((grid_size - 1) * GAP)

    start_x = (window_width - total_grid_width) // 2
    start_y = TOP_MARGIN

    for row in range(grid_size):
        row_tilees = []
        for col in range(grid_size):
            x = start_x + col * (tile_size + GAP)
            y = start_y + row * (tile_size + GAP)
            row_tilees.append(Tile(posX=x, posY=y, dimension=tile_size))
        grid.append(row_tilees)

    for row in range(grid_size):
        for col in range(grid_size - 1):
            tile1 = grid[row][col]
            tile2 = grid[row][col + 1]
            cx = (tile1.rect.right + tile2.rect.left) // 2
            cy = tile1.rect.centery
            connectors.append(
                Connector(
                    cx,
                    cy,
                    (row, col),
                    (row, col + 1),
                    orientation="H",
                    tile_size=tile_size,
                )
            )

    for row in range(grid_size - 1):
        for col in range(grid_size):
            tile1 = grid[row][col]
            tile2 = grid[row + 1][col]
            cx = tile1.rect.centerx
            cy = (tile1.rect.bottom + tile2.rect.top) // 2
            connectors.append(
                Connector(
                    cx,
                    cy,
                    (row, col),
                    (row + 1, col),
                    orientation="V",
                    tile_size=tile_size,
                )
            )

    return grid, connectors


def main():
    pygame.init()

    WINDOW_WIDTH = 700
    WINDOW_HEIGHT = 700
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Mambo")

    BG_COLOR = (20, 27, 35)
    TITLE_COLOR = (255, 255, 255)
    SUBTITLE_COLOR = (180, 190, 200)
    ERROR_COLOR = (224, 122, 122)
    TITLE_SIZE = 60
    SUBTITLE_SIZE = 24
    ERROR_SIZE = 18
    TITLE_Y = 60
    SUBTITLE_Y = 108
    ERROR_Y = 134

    title_font = pygame.font.SysFont("franklingothicdemi", TITLE_SIZE)
    title_surface = title_font.render("MAMBO SOLVER", True, TITLE_COLOR)
    title = title_surface.get_rect(center=(WINDOW_WIDTH // 2, TITLE_Y))

    subtitle_font = pygame.font.SysFont("franklingothicdemi", SUBTITLE_SIZE)
    subtitle_surface = subtitle_font.render("Choose a grid size", True, SUBTITLE_COLOR)
    subtitle = subtitle_surface.get_rect(center=(WINDOW_WIDTH // 2, SUBTITLE_Y))

    error_font = pygame.font.SysFont("franklingothicdemi", ERROR_SIZE)

    design_prompt_surface = subtitle_font.render(
        "Design your grid by clicking on the tiles and between them",
        True,
        SUBTITLE_COLOR,
    )
    design_prompt = design_prompt_surface.get_rect(center=(WINDOW_WIDTH // 2, 108))

    solved_prompt_surface = subtitle_font.render(
        "Solved! Click Next to move on",
        True,
        SUBTITLE_COLOR,
    )
    solved_prompt = solved_prompt_surface.get_rect(center=(WINDOW_WIDTH // 2, 108))

    unsolved_prompt_surface = subtitle_font.render(
        "Cannot be solved! Click next to move on",
        True,
        SUBTITLE_COLOR,
    )
    unsolved_prompt = unsolved_prompt_surface.get_rect(center=(WINDOW_WIDTH // 2, 108))

    button_font = pygame.font.SysFont("franklingothicdemi", 40)

    BUTTON_WIDTH = 300
    BUTTON_HEIGHT = 100
    BUTTON_GAP = 30

    button_6x6 = Button(
        WINDOW_WIDTH // 2 - BUTTON_WIDTH // 2,
        WINDOW_HEIGHT // 2 - BUTTON_HEIGHT - BUTTON_GAP // 2,
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
        "6 x 6",
        button_font,
        (246, 194, 85),
    )

    button_8x8 = Button(
        WINDOW_WIDTH // 2 - BUTTON_WIDTH // 2,
        WINDOW_HEIGHT // 2 + BUTTON_GAP // 2,
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
        "8 x 8",
        button_font,
        (202, 150, 224),
    )

    SOLVE_BUTTON_WIDTH = 300
    SOLVE_BUTTON_HEIGHT = 70

    solve_button = Button(
        WINDOW_WIDTH // 2 - SOLVE_BUTTON_WIDTH // 2,
        610,
        SOLVE_BUTTON_WIDTH,
        SOLVE_BUTTON_HEIGHT,
        "SOLVE",
        button_font,
        (110, 200, 150),
    )

    next_button = Button(
        WINDOW_WIDTH // 2 - SOLVE_BUTTON_WIDTH // 2,
        610,
        SOLVE_BUTTON_WIDTH,
        SOLVE_BUTTON_HEIGHT,
        "NEXT",
        button_font,
        (120, 170, 230),
    )

    state = ScreenState.MENU
    grid_size = None
    grid = []
    connectors = []
    solved = None
    error_message = None

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if state == ScreenState.MENU:
                if button_6x6.handle_event(event):
                    grid_size = 6
                    grid, connectors = create_grid(grid_size, WINDOW_WIDTH)
                    state = ScreenState.DESIGN

                if button_8x8.handle_event(event):
                    grid_size = 8
                    grid, connectors = create_grid(grid_size, WINDOW_WIDTH)
                    state = ScreenState.DESIGN

            elif state == ScreenState.DESIGN:
                for row_tilees in grid:
                    for tile in row_tilees:
                        tile.handle_event(event)

                for connector in connectors:
                    connector.handle_event(event)

                if solve_button.handle_event(event):
                    solved, error_message = solve_mambo(grid_size, grid, connectors)
                    state = ScreenState.SOLVE

            elif state == ScreenState.SOLVE:
                if next_button.handle_event(event):
                    state = ScreenState.MENU

        screen.fill(BG_COLOR)
        screen.blit(title_surface, title)

        if state == ScreenState.MENU:
            screen.blit(subtitle_surface, subtitle)
            button_6x6.display(screen)
            button_8x8.display(screen)

        elif state == ScreenState.DESIGN:
            screen.blit(design_prompt_surface, design_prompt)

            for row_tiles in grid:
                for tile in row_tiles:
                    tile.display(screen)

            for connector in connectors:
                connector.display(screen)

            solve_button.display(screen)

        elif state == ScreenState.SOLVE:
            if solved:
                screen.blit(solved_prompt_surface, solved_prompt)
            else:
                screen.blit(unsolved_prompt_surface, unsolved_prompt)

                if error_message:
                    error_surface = error_font.render(error_message, True, ERROR_COLOR)
                    error_rect = error_surface.get_rect(
                        center=(WINDOW_WIDTH // 2, ERROR_Y)
                    )
                    screen.blit(error_surface, error_rect)

            for row_tiles in grid:
                for tile in row_tiles:
                    tile.display(screen)

            for connector in connectors:
                connector.display(screen)

            next_button.display(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


main()
