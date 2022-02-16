import pygame as py
from Entity import Entity
from json_management import JsonManagement as JM

class Player(Entity):
    def __init__(self, x, y, life):
        super().__init__(x, y, "Adam")
        self.life = self.get_life()
        if self.life == None or self.life == 0:
            self.change_player_life(life)
        
    @staticmethod
    def get_position():
        f = JM.open_file("saves")
        player_position = JM.get_specific_information('["player"]["position"]')
        return player_position
    
    def change_player_position(self):
        current_player_position = [self.rect.x, self.rect.y]
        player_p = JM.open_file("saves")
        
        player_p["player"]["position"] = current_player_position
        
        JM.write_file('saves', player_p)
        
    @staticmethod
    def get_life():
        f = JM.open_file("saves")
        player_position = JM.get_specific_information('["player"]["life"]')
        return player_position
    
    def change_player_life(self, life):
        player_l = JM.open_file("saves")
        
        player_l["player"]["life"] = life
        
        JM.write_file('saves', player_l)
        
    def is_player_dead(self):
        return self.life <= 0