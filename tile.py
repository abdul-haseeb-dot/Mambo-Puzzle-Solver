import pygame


class Tile:
    def __init__(self, posX, posY, dimension):
        self.rect = pygame.Rect(posX, posY, dimension, dimension)
        self.state = 0
        self.is_hovered = False

        self.STATE_COLORS = {0: (51, 56, 62), 1: (246, 194, 85), 2: (202, 150, 224)}
        self.BORDER_COLOR = (73, 80, 88)
        self.BORDER_COLOR_HOVER = (110, 118, 128)
        self.SHAPE_COLOR = (0, 0, 0)
        self.THICKNESS = 4

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            inner_rect = self.rect.inflate(-self.THICKNESS * 2, -self.THICKNESS * 2)
            if inner_rect.collidepoint(event.pos):
                self.change_state()

    def change_state(self):
        self.state = (self.state + 1) % 3

    def display(self, screen):
        fill_color = self.STATE_COLORS[self.state]
        border_color = self.BORDER_COLOR_HOVER if self.is_hovered else self.BORDER_COLOR

        pygame.draw.rect(screen, fill_color, self.rect, border_radius=10)
        pygame.draw.rect(
            screen, border_color, self.rect, self.THICKNESS, border_radius=10
        )

        padding = self.rect.width * 0.25
        cross_thickness = 7
        circle_thickness = 4

        if self.state == 1:
            pygame.draw.line(
                screen,
                self.SHAPE_COLOR,
                (self.rect.left + padding, self.rect.top + padding),
                (self.rect.right - padding, self.rect.bottom - padding),
                cross_thickness,
            )
            pygame.draw.line(
                screen,
                self.SHAPE_COLOR,
                (self.rect.right - padding, self.rect.top + padding),
                (self.rect.left + padding, self.rect.bottom - padding),
                cross_thickness,
            )

        elif self.state == 2:
            radius = (self.rect.width - 2 * padding) / 2
            pygame.draw.circle(
                screen,
                self.SHAPE_COLOR,
                self.rect.center,
                radius,
                circle_thickness,
            )