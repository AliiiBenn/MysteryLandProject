from dataclasses import dataclass
import pygame as py
import pytmx, pyscroll

from objects.tiled_entity import TiledEntity
from entities.player import Player
from entities.npc import Basicnpc, ShopNPC
from database_management import JsonManagement as JM


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
    shops : list[ShopNPC]
    
class MapManager:
    def __init__(self, screen: int, player : str):
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
        
    def check_collisions(self) -> None:
        """vérifie si il ya collision ou non 
        """
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
        
    def teleport_player(self, name : str) -> None:
        """teleporte le joueur

        Args:
            name (str): nom du joueur
        """
        point = self.get_object(name)
        self.player.position[0] = point.x
        self.player.position[1] = point.y
        self.player.save_location()  
        
    def register_map(self, name : str, portals=[] , npcs=[], shops=[]) -> None:
        """boucle principale générant les principales intervenants de la map

        Args:
            name (str): nom de la map
            portals (list, optional): portails présents sur la map. Defaults to [].
            npcs (list, optional): npcs présents sur la map. Defaults to [].
            shops (list, optional): shops présents sur la map. Defaults to [].
        """
        # charger la carte (tmx)
        tmx_data = pytmx.util_pygame.load_pygame(f'Maps/{name}.tmx')
        map_data = pyscroll.data.TiledMapData(tmx_data)
        self.map_layer = pyscroll.orthographic.BufferedRenderer(map_data, self.screen.get_size())
        self.change_zoom(self.screen.get_width(), self.screen.get_height())
        
        
        
        # definir une liste qui va stocker les rectangles de collisions
        walls = []
        AnimatedTile = []
        
        
        
        for obj in tmx_data.objects:
            if obj.type == "collisions":
                walls.append(py.Rect(obj.x, obj.y, obj.width, obj.height))
            elif obj.type == "test":
                AnimatedTile.append(TiledEntity(obj.x, obj.y, obj.name, obj.width, obj.height, 4, 5))
                
        
        # dessiner le groupe de calque
        group = pyscroll.PyscrollGroup(map_layer=self.map_layer, default_layer=6)
        for b in AnimatedTile:
            group.add(b)
        group.add(self.player)
        
        
        for npc in npcs:
            group.add(npc)
        
        # creer un objet map
        self.maps[name] = Map(name, walls, group, tmx_data, portals, npcs, shops)
        
    def change_zoom(self, width: int, height: int) -> dict:
        """change le zomm en fonction du pleine écran ou non

        Args:
            width (int): dimension de le fenetre en largeur
            height (int): dimension de le fenetre en hauteur

        Returns:
            dict: le zomm de la map
        """
        self.map_layer.zoom = 5.6 - ((width + height) / 720)
        return self.map_layer
        
    def get_map(self) -> dict:
        """retourne juste la map actuel

        Returns:
            dict: map actuel
        """
        return self.maps[self.current_map]
    
    def get_group(self) -> dict:
        """retourne groupe de calques

        Returns:
            dict: groupe de calques
        """
        return self.get_map().group
    
    def get_walls(self) -> dict:
        """retourne groupe de murs

        Returns:
            dict: groupe de murs
        """
        return self.get_map().walls
    
    def get_object(self, name: str) -> dict:
        """recoit les objets par nom depuis le fichier tmx

        Args:
            name (str): nom des objets

        Returns:
            dict: objets et leurs noms
        """
        return self.get_map().tmx_data.get_object_by_name(name)
    
    def teleport_npcs(self) -> None:
        """teleport les non player characters
        """
        for map in self.maps:
            map_data = self.maps[map]
            npcs = map_data.npcs
            
            for npc in npcs:
                npc.load_points(map_data.tmx_data)
                npc.teleport_spawn()
    
    def draw(self) -> None:
        """dessine la map
        """
        self.get_group().draw(self.screen)
        self.get_group().center(self.player.rect.center)
        
    def change_map(self) -> None:
        """change la map
        """
        world = JM.open_file("saves")
        
        world["player"]["current_world"] = self.current_map
        
        JM.write_file("saves", world)
        
    def update(self) -> None:
        """met a jour la map avec les npc
        """
        self.get_group().update()
        self.check_collisions()
        
        for npc in self.get_map().npcs:
            npc.move()