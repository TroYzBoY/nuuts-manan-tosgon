"""
Projectile class for game entities
"""
import pygame
import os
import math


class Projectile:
    def __init__(self, x, y, target_x, target_y, damage, is_enemy=False, projectile_type='default'):
        self.x = x
        self.y = y
        self.damage = damage
        self.speed = 8
        self.is_enemy = is_enemy
        self.active = True
        self.projectile_type = projectile_type

        dx = target_x - x
        dy = target_y - y
        length = math.sqrt(dx**2 + dy**2)
        if length > 0:
            self.vel_x = (dx / length) * self.speed
            self.vel_y = (dy / length) * self.speed
        else:
            self.vel_x = 0
            self.vel_y = 0

        # Load appropriate projectile image based on type
        try:
            base_dir = os.path.join(os.path.dirname(
                os.path.abspath(__file__)), '..', 'image')

            if projectile_type == 'fire':
                img_path = os.path.join(base_dir, 'fire_effect.png')
            elif projectile_type == 'water':
                img_path = os.path.join(base_dir, 'water_effect.png')
            elif projectile_type == 'void':
                img_path = os.path.join(base_dir, 'void_effect.png')
            elif projectile_type == 'ice':
                img_path = os.path.join(base_dir, 'ice_effect.png')
            elif projectile_type == 'lightning':
                img_path = os.path.join(base_dir, 'lightning_effect.png')
            elif projectile_type == 'holy':
                img_path = os.path.join(base_dir, 'holy_effect.png')
            else:
                img_path = os.path.join(base_dir, 'projectile.png')

            if os.path.exists(img_path):
                self.image = pygame.image.load(img_path).convert_alpha()
                self.image = pygame.transform.scale(self.image, (20, 20))
            else:
                # Fallback with color coding
                self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
                if projectile_type == 'fire':
                    pygame.draw.circle(self.image, (255, 100, 0), (10, 10), 10)
                elif projectile_type == 'water':
                    pygame.draw.circle(self.image, (0, 150, 255), (10, 10), 10)
                elif projectile_type == 'void':
                    pygame.draw.circle(self.image, (150, 0, 200), (10, 10), 10)
                elif projectile_type == 'ice':
                    pygame.draw.circle(
                        self.image, (150, 200, 255), (10, 10), 10)
                elif projectile_type == 'lightning':
                    pygame.draw.circle(
                        self.image, (255, 255, 100), (10, 10), 10)
                elif projectile_type == 'holy':
                    pygame.draw.circle(
                        self.image, (255, 255, 200), (10, 10), 10)
                else:
                    pygame.draw.circle(self.image, (255, 200, 0), (10, 10), 10)
        except Exception as e:
            print(f"Error loading projectile image: {e}")
            self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 200, 0), (10, 10), 10)

        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.rect.center = (self.x, self.y)

    def check_collision(self, collision_rects):
        """Check if projectile hits a collision tile"""
        for rect in collision_rects:
            if self.rect.colliderect(rect):
                return True
        return False

    def draw(self, surface, camera_x, camera_y):
        surface.blit(self.image, (self.x - camera_x -
                     10, self.y - camera_y - 10))

