import pygame

class Button:
    def __init__(self, x, y, width, height, text, font, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color

        self.TEXT_COLOR = (255, 255, 255)
        self.BORDER_COLOR = tuple(max(0, channel - 60) for channel in color)
        self.BORDER_RADIUS = 12

        self.is_hovered = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def display(self, screen):
        pygame.draw.rect(
            screen, self.color, self.rect, border_radius=self.BORDER_RADIUS
        )

        if self.is_hovered:
            overlay = pygame.Surface(
                (self.rect.width, self.rect.height), pygame.SRCALPHA
            )
            pygame.draw.rect(
                overlay,
                (255, 255, 255, 50),
                overlay.get_rect(),
                border_radius=self.BORDER_RADIUS,
            )
            screen.blit(overlay, self.rect.topleft)

        pygame.draw.rect(
            screen,
            self.BORDER_COLOR,
            self.rect,
            width=2,
            border_radius=self.BORDER_RADIUS,
        )

        text_surface = self.font.render(self.text, True, self.TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)