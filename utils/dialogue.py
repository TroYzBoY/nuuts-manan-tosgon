"""
DialogueSystem class for NPC dialogues
"""
import pygame


class DialogueSystem:
    def __init__(self):
        self.active = False
        self.dialogues = []
        self.current_index = 0
        self.font = pygame.font.Font(None, 28)

    def start_dialogue(self, dialogues):
        self.dialogues = dialogues
        self.current_index = 0
        self.active = len(dialogues) > 0

    def next(self):
        if self.active:
            self.current_index += 1
            if self.current_index >= len(self.dialogues):
                self.active = False
                self.current_index = 0

    def draw(self, surface, screen_width, screen_height):
        if not self.active or not self.dialogues:
            return

        box_height = 120
        box_y = screen_height - box_height - 10
        box_rect = pygame.Rect(10, box_y, screen_width - 20, box_height)

        bg_surf = pygame.Surface((box_rect.width, box_rect.height))
        bg_surf.set_alpha(200)
        bg_surf.fill((20, 20, 40))
        surface.blit(bg_surf, box_rect.topleft)

        pygame.draw.rect(surface, (255, 255, 255), box_rect, 3)

        if self.current_index < len(self.dialogues):
            text = self.dialogues[self.current_index]
            words = text.split(' ')
            lines = []
            current_line = ""
            max_width = box_rect.width - 40

            for word in words:
                test_line = current_line + word + " "
                if self.font.size(test_line)[0] < max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word + " "
            if current_line:
                lines.append(current_line)

            y_offset = box_y + 20
            for line in lines[:3]:
                text_surf = self.font.render(
                    line.strip(), True, (255, 255, 255))
                surface.blit(text_surf, (box_rect.x + 20, y_offset))
                y_offset += 30

        prompt = self.font.render(
            "Press SPACE to continue...", True, (200, 200, 200))
        surface.blit(prompt, (box_rect.x + 20, box_rect.bottom - 35))

