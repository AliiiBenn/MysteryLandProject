import pygame as py

from widgets import DialogBox


class Animations:
    def __init__(self, player, screen):
        self.player = player
        self.screen = screen
        self.width, self.height = self.screen.get_size()
        self.screen_animation_finished = False
        self.distance = 0
        self.dialog_box = DialogBox()
        self.text_box_count = 0
        self.dialog_finished = False
        self.border_position = 0
        self.border_count = 0
        self.border_complete = False

    def teleport_player(self, destination : list[int]) -> None:
        """Méthode permettant de téléporter le joueur à une position donnée pour lancer l'animation

        Args:
            destination (list[int]): la liste des positions x et y du joueur
        """
        self.player.position[0] = destination[0]
        self.player.position[1] = destination[1]

    def render_text_box(self, dialog_list):
        self.text_box_count += 1

        if self.text_box_count >= 20:
            self.dialog_box.render(self.screen)
            if self.text_box_count >= 100:
                self.dialog_box.execute(dialog_list)
                self.text_box_count = 0
        
        
        if self.dialog_box.text_index >= len(dialog_list):
            self.dialog_finished = True
            return True

    def create_screen_border(self, width, height):
        if not self.border_complete:
            self.border_count += 1
            BORDER_SIZE = height // 6
            if not self.border_position >= BORDER_SIZE and self.border_count <= 100:
                self.border_position += 1.5
            if self.border_count >= 100:
                self.border_position -= 1.5
                if self.border_position <= 0:
                    self.border_complete = True
            py.draw.rect(self.screen, (0, 0, 0), (0, 0 - BORDER_SIZE + self.border_position, width, BORDER_SIZE))
            py.draw.rect(self.screen, (0, 0, 0), (0, (height - self.border_position) , width, BORDER_SIZE))
        

    def screen_animation(self, screen):
        self.distance += 5
        py.draw.rect(screen, (0, 0, 0), (0 - self.distance, 0, self.width // 2, self.height))
        py.draw.rect(screen, (0, 0, 0), (self.width // 2 + self.distance, 0, self.width, self.height))
        if self.distance >= self.width // 2:
            self.screen_animation_finished = True
            self.width, self.height = self.screen.get_size()
            return self.screen_animation_finished
        