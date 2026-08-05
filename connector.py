import pygame


class Connector:
    def __init__(self, center_x, center_y, tile1_pos, tile2_pos, orientation, tile_size):
        self.center = (center_x, center_y)
        self.radius = max(6, min(16, round(tile_size * 0.18)))
        self.tile1_pos = tile1_pos
        self.tile2_pos = tile2_pos
        self.orientation = orientation

        self.state = 0
        self.is_hovered = False

        self.COLOR_HOVER = (255, 255, 255, 90)
        self.COLOR_SYMBOL = (0, 0, 0)
        self.COLOR_BORDER = (0, 0, 0)
        self.COLOR_BORDER_HOVER = (90, 90, 90)
        self.COLOR_CIRCLE = (255, 255, 255)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            dx = event.pos[0] - self.center[0]
            dy = event.pos[1] - self.center[1]
            self.is_hovered = (dx * dx + dy * dy) <= (self.radius * self.radius)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            dx = event.pos[0] - self.center[0]
            dy = event.pos[1] - self.center[1]
            if (dx * dx + dy * dy) <= (self.radius * self.radius):
                self.state = (self.state + 1) % 3
                return True
        return False

    def display(self, screen):
        if self.is_hovered:
            overlay = pygame.Surface(
                (self.radius * 2, self.radius * 2), pygame.SRCALPHA
            )
            pygame.draw.circle(
                overlay,
                self.COLOR_HOVER,
                (self.radius, self.radius),
                self.radius,
            )
            screen.blit(
                overlay, (self.center[0] - self.radius, self.center[1] - self.radius)
            )

        if self.state in (1, 2):
            border_color = self.COLOR_BORDER_HOVER if self.is_hovered else self.COLOR_BORDER

            pygame.draw.circle(screen, self.COLOR_CIRCLE, self.center, self.radius)
            pygame.draw.circle(
                screen, border_color, self.center, self.radius, width=2
            )

            cx, cy = self.center
            scale = self.radius / 12

            if self.state == 1:
                line_len = round(5 * scale)
                line_gap = round(3 * scale)
                if self.orientation == "H":
                    pygame.draw.line(
                        screen,
                        self.COLOR_SYMBOL,
                        (cx - line_len, cy - line_gap),
                        (cx + line_len, cy - line_gap),
                        2,
                    )
                    pygame.draw.line(
                        screen,
                        self.COLOR_SYMBOL,
                        (cx - line_len, cy + line_gap),
                        (cx + line_len, cy + line_gap),
                        2,
                    )
                else:
                    pygame.draw.line(
                        screen,
                        self.COLOR_SYMBOL,
                        (cx - line_gap, cy - line_len),
                        (cx - line_gap, cy + line_len),
                        2,
                    )
                    pygame.draw.line(
                        screen,
                        self.COLOR_SYMBOL,
                        (cx + line_gap, cy - line_len),
                        (cx + line_gap, cy + line_len),
                        2,
                    )

            elif self.state == 2:
                offset = round(4 * scale)
                pygame.draw.line(
                    screen,
                    self.COLOR_SYMBOL,
                    (cx - offset, cy - offset),
                    (cx + offset, cy + offset),
                    2,
                )
                pygame.draw.line(
                    screen,
                    self.COLOR_SYMBOL,
                    (cx + offset, cy - offset),
                    (cx - offset, cy + offset),
                    2,
                )