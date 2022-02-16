from dataclasses import dataclass
import pygame as py
import pytmx, pyscroll
from npc import Basicnpc
from json_management import JsonManagement as JM
from player import Player
from TiledEntity import TiledEntity


@dataclass
class Portal:
    from_world : str
    origin_point : str 
    target_world : str
    teleport_point : str 

@dataclass
class Map:
    name : str
    walls : list[py.Rect]
    group : pyscroll.PyscrollGroup
    tmx_data : pytmx.TiledMap
    portals : list[Portal]
    npcs : list[Basicnpc]
    
class MapManager:
    def __init__(self, screen, player):
        self.screen = screen
        self.player = player
        self.maps = dict()
        self.current_map = JM.get_specific_information('["player"]["current_world"]')
        
        self.register_map("World")
        
        if self.current_map == "World":
            self.player.position = Player.get_position()
        else:
            self.teleport_player('player')
        self.teleport_npcs()
            
    # def check_npc_collisions(self, dialog_box):
    #     for sprite in self.get_group().sprites():
    #         if sprite.feet.colliderect(self.player.rect) and type(sprite) is NPC:
    #             dialog_box.execute(sprite.dialog)
        
    def check_collisions(self):
        for portal in self.get_map().portals:
            if portal.from_world == self.current_map:
                point = self.get_object(portal.origin_point)
                rect = py.Rect(point.x, point.y, point.width, point.height)
                
                if self.player.feet.colliderect(rect):
                    copy_portal = portal
                    self.current_map = portal.target_world
                    self.change_map()
                    self.teleport_player(copy_portal.teleport_point)
                    
                    
        for sprite in self.get_group().sprites():
            
            if type(sprite) is Basicnpc:
                if sprite.feet.colliderect(self.player.rect):
                    sprite.speed = 0
                else:
                    sprite.speed = 1
            if not isinstance(sprite, TiledEntity):
                if sprite.feet.collidelist(self.get_walls()) > - 1:
                    sprite.move_back()
        
    def teleport_player(self, name):
        point = self.get_object(name)
        self.player.position[0] = point.x
        self.player.position[1] = point.y
        self.player.save_location()  
        
    def register_map(self, name, portals=[], npcs=[]):
        # charger la carte (tmx)
        tmx_data = pytmx.util_pygame.load_pygame(f'Maps/{name}.tmx')
        map_data = pyscroll.data.TiledMapData(tmx_data)
        map_layer = pyscroll.orthographic.BufferedRenderer(map_data, self.screen.get_size())
        map_layer.zoom = 2.5
        
        
        
        # definir une liste qui va stocker les rectangles de collisions
        walls = []
        
        for obj in tmx_data.objects:
            if obj.type == "collisions":
                walls.append(py.Rect(obj.x, obj.y, obj.width, obj.height))
            elif obj.type == "b":
                # py.draw.rect(self.screen, (0, 0, 255), (obj.x, obj.y, obj.width, obj.height))
                self.butterfly = TiledEntity(obj.x, obj.y, "animated_butterfly_2_32x32", obj.width, obj.height, 4, 5)
                
        
        # dessiner le groupe de calque
        group = pyscroll.PyscrollGroup(map_layer=map_layer, default_layer=6)
        group.add(self.player)
        group.add(self.butterfly)
        
        for npc in npcs:
            group.add(npc)
        
        # creer un objet map
        self.maps[name] = Map(name, walls, group, tmx_data, portals, npcs)
        
    def get_map(self):
        return self.maps[self.current_map]
    
    def get_group(self):
        return self.get_map().group
    
    def get_walls(self):
        return self.get_map().walls
    
    def get_object(self, name):
        return self.get_map().tmx_data.get_object_by_name(name)
    
    def teleport_npcs(self):
        for map in self.maps:
            map_data = self.maps[map]
            npcs = map_data.npcs
            
            for npc in npcs:
                npc.load_points(map_data.tmx_data)
                npc.teleport_spawn()
    
    def draw(self):
        self.get_group().draw(self.screen)
        self.get_group().center(self.player.rect.center)
        
    def change_map(self):
        world = JM.open_file("saves")
        
        world["player"]["current_world"] = self.current_map
        
        JM.write_file("saves", world)
        
    def update(self):
        self.get_group().update()
        self.check_collisions()
        
        for npc in self.get_map().npcs:
            npc.move()
            # test