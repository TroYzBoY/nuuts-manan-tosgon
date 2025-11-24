"""
FloatingText class for UI effects
"""
import pygame


class FloatingText:
    def __init__(self, x, y, text, color=(255, 0, 0)):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.timer = 60
        self.vel_y = -2
        self.alpha = 255

    def update(self):
        self.y += self.vel_y
        self.timer -= 1
        self.alpha = int((self.timer / 60) * 255)

    def draw(self, surface, camera_x, camera_y):
        if self.timer > 0:
            font = pygame.font.Font(None, 36)
            text_surf = font.render(self.text, True, self.color)
            text_surf.set_alpha(self.alpha)
            surface.blit(text_surf, (self.x - camera_x, self.y - camera_y))

    def is_alive(self):
        return self.timer > 0

