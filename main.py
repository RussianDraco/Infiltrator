###NOTICES/INFORMATION###
# inspired by Micheal Reeves


"""
To make it easier to navigate, the code is separated into sections with triple hashtag comments
Classes are more widely used to create simplicity
"""
###IMPORTS###

import pygame as pg
import sys
import math
import os
from collections import deque
from random import randint, random, choice, uniform
import json
from pyautogui import size as pyautosize
#import numpy as np

###BASIC FUNCTIONS###
#distance formula func
def distance_formula(x1, y1, x2, y2):
    return math.sqrt((x1-x2)**2 + (y1-y2)**2)

#returns a list of numbers for the distance of each numbers in the input list from the input num
def number_distances(ar, num):
    return [abs(i-num) for i in ar]

#returns json dict
def get_json(path):
    with open(path) as json_file:
        data = json.load(json_file)
    json_file.close()
    return data

#rotate an image
def rotate_image(image, angle):
    loc = image.get_rect().center
    rot_sprite = pg.transform.rotate(image, angle)
    rot_sprite.get_rect().center = loc
    return rot_sprite

#get obj from dict, if its not there, return none instead of invoking an error
def none_get(dict, obj):
    try:
        return dict[obj]
    except KeyError:
        return None

###SETTINGS###

RANDOM_GENERATION = False #if true, portals will generate random mazes, else, player made mazes will be used(from levels.json)

# screen settings
RES = WIDTH, HEIGHT = 1600, 700 #1600, 700 is default, i might change it for simplicity sake
ACTUALRES = RWIDTH, RHEIGHT = pyautosize()

# screen ratios between actual and player screen
RatioWidth = WIDTH/RWIDTH
RatioHeight = HEIGHT/RHEIGHT

#statbar settings
STATBARRES = SWIDTH, SHEIGHT = WIDTH, 150 #WIDTH, 150 is default

# RES = WIDTH, HEIGHT = 1920, 1080

#some other variables
HALF_WIDTH = WIDTH // 2
HALF_HEIGHT = HEIGHT // 2
FPS = 60

#player vars
PLAYER_POS = 1.5, 1.5  # cur_map
PLAYER_ANGLE = 0
PLAYER_SPEED = 0.0055
PLAYER_ROT_SPEED = 0.002
PLAYER_SIZE_SCALE = 60

LOSING_STEALTH = 15

#stamina stuff
PLAYER_MAX_STAMINA = 100
STAMINA_RECOVERY_DELAY = 250

#inventory
INVENTORY_SIZE = 9

#mouse vars
MOUSE_SENSITIVITY = 0.0003
def recalibrate_sensitivity(mouseOn): global MOUSE_SENSITIVITY; MOUSE_SENSITIVITY = 0.0003 if not mouseOn else 0.0002

MOUSE_MAX_REL = 40
MOUSE_BORDER_LEFT = 100
MOUSE_BORDER_RIGHT = WIDTH - MOUSE_BORDER_LEFT

#color of stuff
FLOOR_COLOR = (30, 30, 30)
SUSFONT_COLOR = (204, 202, 169)

#fov stuff
FOV = math.pi / 3
HALF_FOV = FOV / 2
NUM_RAYS = WIDTH // 2
HALF_NUM_RAYS = NUM_RAYS // 2
DELTA_ANGLE = FOV / NUM_RAYS
MAX_DEPTH = 20

#scaling and screen distance
SCREEN_DIST = HALF_WIDTH / math.tan(HALF_FOV)
SCALE = WIDTH // NUM_RAYS

#texture variables
TEXTURE_SIZE = 256
HALF_TEXTURE_SIZE = TEXTURE_SIZE // 2

#icon vars
ICON_WIDTH, ICON_HEIGHT = 80, 80

#check if youre touching an enemy to give you suspicion every this much time
TOUCH_CHECK_TIME = 5000

#changeable settings
MouseRotation_Setting = False

##STATS##
class Stats: #just a class to store npc stats
    def __init__(self, vision_dist, suspicion_lvl, speed, minsus, random_walk = False, follower = False, size = 1):
        self.vision_dist = vision_dist #how far the enemy can see the player
        self.suspicion_lvl = suspicion_lvl #how suspicious the npc gets of the player (1-5)
        self.speed = speed #how fast the enemy walks
        self.follower = follower
        self.minsus = minsus
        self.size = size
        self.random_walk = random_walk

##ITEMS##
class Item:
    def __init__(self, name, icon, id, desc=""):
        self.id = id
        self.name = name
        self.desc = desc
        self.icon = icon

#contains all the possible items
ITEM_DICT = {
    1 : Item("Disguise", 'resources/sprites/items/disguise.png', 1, ""),
    2 : Item("Meme1", 'resources/sprites/memes/meme1.png', 2, ""),
    3 : Item("Meme1", 'resources/sprites/memes/meme2.png', 3, ""),
    4 : Item("Meme1", 'resources/sprites/memes/meme3.png', 4, ""),
    5 : Item("Meme1", 'resources/sprites/memes/meme4.png', 5, ""),
    6 : Item("Meme1", 'resources/sprites/memes/meme5.png', 6, "")
}

#dict describing all the enemies
ENEMIES = {
    #guy who opens his mouth
    "businessman": {
        "path" : 'resources/sprites/npc/businessman/0.png',
        "scale": 0.6,
        "shift" : 0.38,
        "animation_time" : 180,
        "stats" : Stats(
            vision_dist = 2,
            suspicion_lvl = 2,
            speed = 0.01,
            minsus = 6,
            random_walk = True
        )
    },
    "janitor": {
        "path" : 'resources/sprites/npc/janitor/0.png',
        "scale": 0.6,
        "shift" : 0.38,
        "animation_time" : 180,
        "stats" : Stats(
            vision_dist = 1,
            suspicion_lvl = 1,
            speed = 0.01,
            minsus = 10,
            random_walk = True
        )
    },
    "coffeeman": {
        "path" : 'resources/sprites/npc/coffeeman/0.png',
        "scale": 0.6,
        "shift" : 0.38,
        "animation_time" : 180,
        "stats" : Stats(
            vision_dist = 3,
            suspicion_lvl = 2,
            speed = 0.02,
            minsus = 5,
            random_walk = True
        )
    },
    "octopus": {
        "path" : 'resources/sprites/npc/octopus/0.png',
        "scale": 0.6,
        "shift" : 0.38,
        "animation_time" : 180,
        "stats" : Stats(
            vision_dist = 1,
            suspicion_lvl = 2,
            speed = 0.01,
            minsus = 9,
            random_walk = True
        )
    },
    "secretary": {
        "path" : 'resources/sprites/npc/secretary/0.png',
        "scale": 0.6,
        "shift" : 0.45,
        "animation_time" : 180,
        "stats" : Stats(
            vision_dist = 1,
            suspicion_lvl = 3,
            speed = 0.01,
            minsus = 4,
            random_walk = True
        )
    },
    "alien": {
        "path" : 'resources/sprites/npc/alien/0.png',
        "scale": 0.6,
        "shift" : 0.45,
        "animation_time" : 180,
        "stats" : Stats(
            vision_dist = 1,
            suspicion_lvl = 3,
            speed = 0.01,
            minsus = 4,
            random_walk = True
        )
    },
    "goku": {
        "path" : 'resources/sprites/npc/goku/0.png',
        "scale": 1,
        "shift" : 0.1,
        "animation_time" : 180,
        "stats" : Stats(
            vision_dist = 999,
            suspicion_lvl = 5,
            speed = 0.05,
            minsus = 0
        )
    }
}


###PLAYER###


#player class
class Player:
    #define class variables when instanced
    def __init__(self, game):
        self.game = game
        self.x, self.y = BASE_DATA["spawn"][0], BASE_DATA["spawn"][1]
        self.angle = 1e-6
        self.rel = pg.mouse.get_rel()[0]
        self.time_prev = pg.time.get_ticks()
        self.canMove = True

        self.stealth = 0

        self.criminal_stealth = False

        self.stamina = PLAYER_MAX_STAMINA

        self.time_prev = pg.time.get_ticks()

        self.floor_level = 7

        self.inventoryOpen = False

        self.onPortal = False
        #self.onRandom = False

    def teleport(self, x, y = None):
        if type(x) == type(['a']):
            self.x = x[0]; self.y = x[1]
            return
        
        elif type(x) == type((1, 2)):
            self.x, self.y = x
            return

        self.x = x; self.y = y

    def portal_check(self):
        if distance_formula(PORTAL_X, PORTAL_Y, self.x, self.y) < 1.25:
            self.game.map.entered_portal()
            return True
        return False

    def random_check(self):
        if self.game.map.inBase and distance_formula(Random_Portal_X, Random_Portal_Y, self.x, self.y) < 1.25:
            self.game.map.entered_portal(True)
            return True
        return False
    
    def check_stamina_recovery_delay(self):
        time_now = pg.time.get_ticks()
        if time_now - self.time_prev > STAMINA_RECOVERY_DELAY:
            self.time_prev = time_now
            return True

    def recover_stamina(self):
        if self.check_stamina_recovery_delay() and self.stamina < PLAYER_MAX_STAMINA:
            self.stamina += 1

    def check_touching_sus(self):
        if self.game.check_touching_trigger:
            if self.game.object_handler.npc_on_square(self.map_pos) != None:
                self.raise_suspicion(1)

    #function to move player
    def movement(self):
        if not self.canMove or self.inventoryOpen:
            return

        #mesure trigonometric numbers
        sin_a = math.sin(self.angle)
        cos_a = math.cos(self.angle)

        #define potential movement and set speed
        dx, dy = 0, 0

        #define dictionary with key statuses
        keys = self.game.keys

        if keys[pg.K_LSHIFT]:
            if self.game.player.stamina >= 5:
                self.game.player.stamina -= 1
                speed = PLAYER_SPEED * self.game.delta_time * 1.25 
            else:
                speed = PLAYER_SPEED * self.game.delta_time
        else:
            speed = PLAYER_SPEED * self.game.delta_time

        #speed times trig nums
        speed_sin = speed * sin_a
        speed_cos = speed * cos_a

        #check key movements and add potential to potential movement on x and y axis
        if keys[pg.K_w]:
            dx += speed_cos
            dy += speed_sin
        if keys[pg.K_s]:
            dx -= speed_cos
            dy -= speed_sin
        if keys[pg.K_a]:
            dx += speed_sin
            dy -= speed_cos
        if keys[pg.K_d]:
            dx -= speed_sin
            dy += speed_cos

        #check that potential movement dosent go into wall
        self.check_wall_collision(dx, dy)

        #self.rel is used for rendering the sky

        #turning with arrows
        if not MouseRotation_Setting:
            if keys[pg.K_LEFT]:
                self.angle -= PLAYER_ROT_SPEED * self.game.delta_time
            if keys[pg.K_RIGHT]:
                self.angle += PLAYER_ROT_SPEED * self.game.delta_time
            self.angle %= math.tau
            self.rel = self.angle * 5.1

    #function for checking if pos is wall
    def check_wall(self, x, y):
        if self.game.map.inBase:
            return (x, y) not in self.game.map.world_map# and not (x, y) in ALL_EMPTY_COLLIDER
        else:
            return (x, y) not in self.game.map.world_map
    
    #check if potential movement goes into wall
    def check_wall_collision(self, dx, dy):
        scale = PLAYER_SIZE_SCALE / self.game.delta_time

        if self.check_wall(int(self.x + dx * scale), int(self.y)):
            self.x += dx
        if self.check_wall(int(self.x), int(self.y + dy * scale)):
            self.y += dy

    #debug thingy
    def draw(self):
        def triangle_calc(pos, ang, sideL): #mesures vertices of a triangle thats centered and points with an angle
            return[(pos[0] + sideL * math.cos(ang), pos[1] + sideL * math.sin(ang)),
                   (pos[0] + sideL * math.cos(ang + 2*math.pi/3), pos[1] + sideL * math.sin(ang + 2*math.pi/3)),
                   (pos[0] + sideL * math.cos(ang + 4*math.pi/3), pos[1] + sideL * math.sin(ang + 4*math.pi/3))]

        points = triangle_calc([100, 600], self.angle, 10)

        #elongates one angle to show direction easier
        elon_poX, elon_poY = points[0]
        elon_poX += math.cos(self.angle) * 5; elon_poY += math.sin(self.angle) * 5
        points[0] = elon_poX, elon_poY

        pg.draw.polygon(self.game.screen, (255, 20, 20), [points[0], points[1], points[2]])

    #function for looking around with mouse
    def mouse_control(self):
        if not self.canMove or self.inventoryOpen:
            self.rel = 0
            return

        mx, my = pg.mouse.get_pos()
        if mx < MOUSE_BORDER_LEFT or mx > MOUSE_BORDER_RIGHT:
            pg.mouse.set_pos([HALF_WIDTH, HALF_HEIGHT])
        self.rel = pg.mouse.get_rel()[0]
        self.rel = max(-MOUSE_MAX_REL, min(MOUSE_MAX_REL, self.rel))
        self.angle += self.rel * MOUSE_SENSITIVITY/2 * self.game.delta_time
        self.angle %= math.tau

    def raise_suspicion(self, pnts):
        self.stealth += pnts
        if self.stealth >= LOSING_STEALTH:
            self.criminal_stealth = True

    def check_lose_game(self):
        if self.criminal_stealth and self.game.object_handler.npc_on_square(self.map_pos) != None:
            self.game.lose_game()

    #update function for player class
    def update(self):
        self.onPortal = self.portal_check()
        self.check_lose_game()
        self.check_touching_sus()
        #self.onRandom = self.random_check()
        self.movement()
        self.recover_stamina()

        if MouseRotation_Setting:
            self.mouse_control()

    #check position
    @property #as i understand, this provides an easier way to retrieve class properties
    def pos(self):
        return self.x, self.y
    
    #check position on map
    @property
    def map_pos(self):
        return int(self.x), int(self.y)


###INVENTORY###


class InventorySystem:
    def __init__(self, game):
        self.game = game
        self.inventory = {} #a dictionary of Item's that would work as Item : quantity

    #get an item class by its id
    def get_item_by_id(self, id):
        return ITEM_DICT[id]

    #get an item class by its name
    def get_item_by_name(self, name):
        for itm in ITEM_DICT:
            if ITEM_DICT[itm].name.lower() == name.lower():
                return ITEM_DICT[itm]
        return None

    #check if item is in the inventory
    def in_inventory(self, item):
        if item in self.inventory:
            return True
        return False

    def num_in_inventory(self, item, quan):
        if item in self.inventory:
            if self.inventory[item] >= quan:
                return True
        return False

    #add an item to the inventory
    def add_item(self, itm, quan):
        if itm in self.inventory:
            self.inventory[itm] = self.inventory[itm] + quan
        else:
            self.inventory[itm] = quan
        return True #should return false in this function if no inventory space

    #remove an item from the inventory
    def remove_item(self, itm, quan):
        if not itm in self.inventory:
            return False
        
        if self.inventory[itm] > quan:
            self.inventory[itm] = self.inventory[itm] - quan
            return True

        elif self.inventory[itm] == quan:
            self.inventory.pop(itm)
            return True

        else:
            return False
        
    def meme_number(self):
        num = 0
        for itm in self.inventory:
            if 'meme' in itm.name:
                num += 1
        return num


###MAP###

##MAZE GENERATION##

class MazeGenerator:
    def __init__(self):
        pass

    def generate_maze(self, w, h, diff): #diff is difficulty, 0 is peaceful, the higher, the harder
        def resetMaze(ar):
            nI = 0
            nJ = 0
            for r in ar:
                nI = 0
                for s in r:
                    ar[nJ][nI] = 1
                    nI+=1
                nJ+=1
            return ar

        def isMazeValid(ar, w_, h_, finder = False, startpos = (0,0)):
            #for y_ in range(h_):
            #    for x_ in range(w_)

            seen = set([startpos])
            queue = [startpos]

            while queue:
                i,j = queue.pop(0)
                seen.add((i, j))
                for di, dj in [(1,0),(-1,0),(0,1),(0,-1)]:
                    ni, nj = i+di, j+dj

                    if (ni, nj) in seen:
                        continue

                    if ni<0 or nj<0 or ni>=w_ or nj>=h_:
                        continue

                    try:
                        if ar[ni][nj] == "p":
                            if finder:
                                return True, list(seen)
                            return True
                    except IndexError:
                        continue

                    if ar[ni][nj] == 1:
                        continue

                    if ar[ni][nj] == 0:
                        seen.add((ni,nj))
                        queue.append((ni,nj))
            
            return False
        
        def filter_seen_set(mz, st):
            ar = list(st)

            n = 0
            for (y, x) in ar:
                ar[n] = (x, y)
                n+=1

            outar = []

            for (x, y) in ar:
                if mz[y][x] == 0:
                    outar.append((x+1.5, y+1.5))

            return outar

        maze = []

        for y in range(h-2):
            addar = []
            for x in range(w-2):
                addar.append(1)
            maze.append(addar)

        x2, y2 = 0, 0

        ran = randint(0, (w-2)*(h-2)-1)
        x2, y2 = ran % (w-2), math.floor(ran/(w-2))
        maze[y2][x2] = "p"

        e = 0
        while not isMazeValid(maze, w-2, h-2):
            while not maze[y2][x2] == 1:
                ran = randint(0, (w-2)*(h-2)-1)
                x2, y2 = ran % (w-2), math.floor(ran/(w-2))
            maze[y2][x2] = 0
            e+=1

            if e >= round((w-2) * (h-2) * 0.75):
                maze = resetMaze(maze)
                x2, y2 = 0, 0

                ran = randint(0, (w-2)*(h-2)-1)
                x2, y2 = ran % (w-2), math.floor(ran/(w-2))
                maze[y2][x2] = "p"
                e = 0

        t, s = isMazeValid(maze, w-2, h-2, finder = True)
        empties = filter_seen_set(maze, s)

        spawn = choice(empties)

        x,y = spawn
        if not maze[int(y-1.5)][int(x-1.5)] == 0:
            while not maze[int(y-1.5)][int(x-1.5)] == 0:
                spawn = choice(empties)
                x,y = spawn

        empties.remove(spawn)

        n = 0
        for r in maze:
            n_r = [1]
            for s in r:
                n_r.append(s)
            n_r.append(1)
            maze[n] = n_r
            n+=1

        top_down_padding = []

        for x in range(w):
            top_down_padding.append(1)

        final_maze = [top_down_padding]

        for r in maze:
            final_maze.append(r)
        final_maze.append(top_down_padding)

        portal_loc = None

        for y, r in enumerate(final_maze):
            for x, v in enumerate(r):
                if final_maze[y][x] == "p":
                    portal_loc = x, y

        if diff == 0:
            return [final_maze, spawn, portal_loc, {}]

        return [final_maze, spawn, portal_loc]


#define map
#false for nothing, numbers for different textures and "p"
_ = False
P = "p"
R = "r"
base_map = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, _, _, _, _, _, _, _, _, _, 3, 2, 2, 2, _, 1],
    [1, _, _, _, _, _, _, _, _, _, 2, _, _, _, 2, 1],
    [1, _, _, _, _, _, _, _, _, _, 2, _, _, _, 2, 1],
    [1, _, _, _, _, _, _, _, _, _, _, _, _, _, P, 1],
    [1, _, _, _, _, _, _, _, _, _, 2, _, _, _, 2, 1],
    [1, _, _, _, _, _, _, _, _, _, 2, _, _, _, _, 1],
    [1, _, _, _, _, _, _, _, _, _, 3, 2, 2, 2, _, 1],
    [1, 1, _, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [3, _, _, _, _, _, _, 3, 1, _, _, _, _, _, _, _],
    [1, _, _, _, _, _, _, 5, 1, _, _, _, _, _, _, _],
    [5, _, _, _, _, _, _, 5, 1, _, _, _, _, _, _, _],
    [5, _, _, _, _, _, _, 5, 1, _, _, _, _, _, _, _],
    [5, _, _, _, _, _, _, 5, 1, _, _, _, _, _, _, _],
    [5, _, _, _, _, _, _, 5, 1, _, _, _, _, _, _, _],
    [5, _, _, _, _, _, _, 5, 1, _, _, _, _, _, _, _],
    [1, 1, 1, 1, 1, 5, 5, 1, 1, _, _, _, _, _, _, _]
    #0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16
]

Random_Portal_X, Random_Portal_Y = 14, 14

#info abt the bloated goblin that is removed with a stomach medicine

#map info for the spawn/base/home
BASE_DATA = {
    "map": base_map,
    "portal": [14.5, 4.5],
    "spawn": [1.5, 1.5],
    "spawns": {
        "npc": [
            ["janitor", [3.5, 3.5]],
            #["businessman", [2.5, 2.5]],
            #["coffeeman", [4.5, 2.5]],
            #["octopus", [4.5, 3.5]],
            #["secretary", [5.5, 2.5]],
            ["alien", [5.5, 3.5]],
            #["goku", [3.5, 2.5]]
        ],
        "passive": [],
        "sprites": [
            #['resources/sprites/static/coolio.png', [4.5, 4.5], 0.7, 0.5],
            #['resources/sprites/static/plant.png', [3.5, 3.5], 0.4, 1],
            #['resources/sprites/static/plant2.png', [5.5, 5.5], 0.5, 0.7],
            #['resources/sprites/static/fridge.png', [5.5, 3], 1.3, 0.1],
            #['resources/sprites/static/aquarium.png', [4.5, 3], 1, 0.3],
            #['resources/sprites/static/chair.png', [2.5, 3], 0.7, 0.5]
            #['resources/sprites/static/candlebra.png', [2.5, 2.5], 0.25, 1.4]
        ],
        "pickups": [
            [[6.5, 5.5], 'sus', 'resources/sprites/items/disguise.png', -3, 0.5, 0.7, ""],
            [[6.5, 6.5], 'item', None, 1, 0.5, 0.7, 2]
        ]
    }
}

#portal coords have to always be the square from which you teleport not the actual portal location
PORTAL_X, PORTAL_Y = 15, 4

cur_map = None

LEVEL_DATA = get_json('resources/json/levels.json')

#   for ALL_EMPTY_COLLIDERS, when adding an empty collider, you need to go into the game and check the position 
#   of where you actually want to put it because it sometimes registers differently then seen on map, LIKE ONE OFF ON THE X OR Y AXIS THEN WHAT IT LOOKS LIKE

#   if you want to be lazy, you can change the wall collision code in player class so that it considers the squares around an empty collider square also impermeable so that you dont have to check all of them

#   cough, cough, never mind the last three lines, idk if they actually apply because i kinda counted wrong when making the location for the empty collider square...

# need to add all empty colliders here, if there is a coordinate here, it will not be able to be walked through, do not forget coordinates start from 1, y increases downwards, x increases to the right
ALL_EMPTY_COLLIDER = [(14, 7)]

#map class
class Map:
    #store some variables, this class is mostly used for fetching map vars
    def __init__(self, game):
        self.game = game

        #var to hold spawn dict until object handler is generated to actaully spawn them
        self.need_to_load = None
        self.load_base()

        #minimap offsets
        self.mmxoffset = 0
        self.mmyoffset = 0
        self.mmsurface = pg.Surface((100, 100))

        self.cur_map = cur_map
        self.world_map = {}
        self.rows = len(self.cur_map)
        self.cols = len(self.cur_map[0])
        self.current_level = 1
        self.inBase = True

        self.generator = MazeGenerator()

        self.inRandom = False

        self.get_map()

    def EXPIREMENTAL_GENERATION(self):
        synth_map, spwn, portal, spawn_dict = self.generator.generate_maze(30, 30, 7)
        self.game.object_handler.clear_entities(); self.game.object_handler.clear_entities()
        self.game.player.teleport(spwn)
        self.load_synthetic_map(synth_map, portal, spawn_dict)
        self.game.pathfinding.reset_pathfinding(self.cur_map)
        self.inBase = False

    def entered_portal(self):
        #if not self.inBase:
        #    self.game.player.teleport(BASE_DATA["spawn"])
        #    self.load_base()
        #    self.game.pathfinding.reset_pathfinding(self.cur_map)
        #    self.inBase = True
        #    self.inRandom = False
        #    return

        #if self.inBase:
        try:
            self.game.player.teleport(LEVEL_DATA[str(self.current_level)]["spawn"]) #---
            self.load_level(self.current_level)
            self.game.pathfinding.reset_pathfinding(self.cur_map)
            self.current_level += 1
        except KeyError as x:
            print(x)
            self.game.win_game()

        #self.inBase = False
        #else:
        #    self.game.player.teleport(BASE_DATA["spawn"])
        #    self.load_base()
        #    self.current_level += 1
        #    self.game.pathfinding.reset_pathfinding(self.cur_map)
        #    self.inBase = True

    def get_map(self):
        #reset world map maybe?
        for j, row in enumerate(self.cur_map):
            for i, value in enumerate(row):
                if value or not value == 0:
                    self.world_map[(i, j)] = value

    def load_base(self):
        lvldata = BASE_DATA
        lvlmap, lvlspawn = lvldata["map"], lvldata["spawns"]

        global PORTAL_X, PORTAL_Y
        PORTAL_X, PORTAL_Y = BASE_DATA["portal"][0], BASE_DATA["portal"][1]

        self.change_map(lvlmap, base=True)
        try:
            self.game.object_handler.load_level_spawns(lvlspawn)
        except AttributeError:
            self.need_to_load = lvlspawn

        if self.game.sound_player.is_sound_playing("themealt"):
            self.game.sound_player.stop_sound("themealt")
            self.game.sound_player.play_sound("theme")

    def change_map(self, newmap, texture_offset = None, base = False): #should update to new map
        global cur_map

        if not texture_offset == None and not base:
            inttype = type(1)
            for y, r in enumerate(newmap):
                for x, v in enumerate(r):
                    if type(newmap[y][x]) == inttype and not newmap[y][x] == 0:
                        newmap[y][x] = int(v) + texture_offset

        cur_map = newmap

        self.cur_map = cur_map
        self.world_map = {}
        self.rows = len(self.cur_map)
        self.cols = len(self.cur_map[0])

        self.get_map()
    
    def load_level(self, lvl_num):
        lvldata = LEVEL_DATA[str(lvl_num)]
        lvlmap, lvlspawn = lvldata["map"], lvldata["spawns"]
        try:
            portalLoc = lvldata["portal"]
        except KeyError:
            portalLoc = -99, -99

        global PORTAL_X, PORTAL_Y
        PORTAL_X, PORTAL_Y = portalLoc[0], portalLoc[1]

        self.change_map(lvlmap, none_get(lvldata, "textureOffset"))
        try:
            self.game.object_handler.load_level_spawns(lvlspawn)
        except AttributeError:
            self.need_to_load = lvlspawn

    def load_synthetic_map(self, synthmap, portal, spawndict): #for generated maps
        lvlmap = synthmap

        global PORTAL_X, PORTAL_Y
        PORTAL_X, PORTAL_Y = portal

        self.change_map(lvlmap)
        try:
            self.game.object_handler.load_level_spawns(spawndict)
        except AttributeError:
            self.need_to_load = spawndict

    #minimap thinkgy
    def draw(self):
        pass
    #    self.mmsurface.fill('black')
    #    self.mmxoffset = -self.game.player.x; self.mmyoffset = -self.game.player.y
    #    [pg.draw.rect(self.mmsurface, 'darkgray', (pos[0] * 20 + self.mmxoffset * 20 + 50, pos[1] * 20 + self.mmyoffset * 20 + 50, 20, 20), 2) for pos in self.world_map]
    #    self.game.screen.blit(self.mmsurface, (50, 550))
        

###RAYCASTING###


#raycasting class
class RayCasting:
    #on init function, def vars
    def __init__(self, game):
        self.game = game
        self.ray_casting_result = []
        self.objects_to_render = []
        self.textures = self.game.object_renderer.wall_textures

    #function to compile list of things to render
    def get_objects_to_render(self):
        self.objects_to_render = []
        #propagates through rays and their results
        for ray, values in enumerate(self.ray_casting_result):
            depth, proj_height, texture, offset = values

            if proj_height < HEIGHT:
                wall_column = self.textures[texture].subsurface(
                    offset * (TEXTURE_SIZE - SCALE), 0, SCALE, TEXTURE_SIZE
                )
                wall_column = pg.transform.scale(wall_column, (SCALE, proj_height))
                wall_pos = (ray * SCALE, HALF_HEIGHT - proj_height // 2)
            else:
                texture_height = TEXTURE_SIZE * HEIGHT / proj_height
                wall_column = self.textures[texture].subsurface(
                    offset * (TEXTURE_SIZE - SCALE), HALF_TEXTURE_SIZE - texture_height // 2,
                    SCALE, texture_height
                )
                wall_column = pg.transform.scale(wall_column, (SCALE, HEIGHT))
                wall_pos = (ray * SCALE, 0)

            #adds to the list of things to render the piece of wall to render
            self.objects_to_render.append((depth, wall_column, wall_pos))

    #main raycasting func
    def ray_cast(self):
        #list of raycasting results, player pos and player pos on map
        self.ray_casting_result = []
        ox, oy = self.game.player.pos
        x_map, y_map = self.game.player.map_pos

        #vertical and horizontal for textures
        texture_vert, texture_hor = 1, 1

        #define first ray angle
        ray_angle = self.game.player.angle - HALF_FOV + 0.0001
        #loop for every ray emission
        #dx and dy are increments to move to the next grid horizontal/vertical line
        for ray in range(NUM_RAYS):
            #trig nums
            sin_a = math.sin(ray_angle)
            cos_a = math.cos(ray_angle)

            #doing horizontal rays
            y_hor, dy = (y_map + 1, 1) if sin_a > 0 else (y_map - 1e-6, -1)

            depth_hor = (y_hor - oy) / sin_a
            x_hor = ox + depth_hor * cos_a

            delta_depth = dy / sin_a
            dx = delta_depth * cos_a

            for i in range(MAX_DEPTH):
                tile_hor = int(x_hor), int(y_hor)
                if tile_hor in self.game.map.world_map:
                    texture_hor = self.game.map.world_map[tile_hor]
                    break
                x_hor += dx
                y_hor += dy
                depth_hor += delta_depth

            #doing vertical rays
            x_vert, dx = (x_map + 1, 1) if cos_a > 0 else (x_map - 1e-6, -1)

            depth_vert = (x_vert - ox) / cos_a
            y_vert = oy + depth_vert * sin_a

            delta_depth = dx / cos_a
            dy = delta_depth * sin_a

            for i in range(MAX_DEPTH):
                tile_vert = int(x_vert), int(y_vert)
                if tile_vert in self.game.map.world_map:
                    texture_vert = self.game.map.world_map[tile_vert]
                    break
                x_vert += dx
                y_vert += dy
                depth_vert += delta_depth

            #depth, texture offset
            if depth_vert < depth_hor:
                depth, texture = depth_vert, texture_vert
                y_vert %= 1
                offset = y_vert if cos_a > 0 else (1 - y_vert)
            else:
                depth, texture = depth_hor, texture_hor
                x_hor %= 1
                offset = (1 - x_hor) if sin_a > 0 else x_hor

            #remove fisheye effect
            depth *= math.cos(self.game.player.angle - ray_angle)

            #debug thingy -> pg.draw.line(self.game.screen, 'yellow', (100 * ox, 100 * oy), (100 * ox + 100 * depth * cos_a, 100 * oy + 100 * depth * sin_a), 2)

            #mesure the height of the projection
            proj_height = SCREEN_DIST/(depth + 0.0001)

            #ray casting result appened to the array that will be drawn
            self.ray_casting_result.append((depth, proj_height, texture, offset))

            #add to angle to go to next ray's angle
            ray_angle += DELTA_ANGLE

    #update raycasting class
    def update(self):
        self.ray_cast()
        self.get_objects_to_render()


###TEXT BOX###


class TextBox:
    def __init__(self, game, x, y, width, height):
        self.pos = x, y

        self.rect = pg.Rect(x, y, width, height)
        self.game = game
        self.shog = False
        self.writing = False
        self.text = ""
        self.font = pg.font.Font('resources/textutil/textboxfont.ttf', 30)
        img = pg.image.load('resources/textutil/textbox.png').convert_alpha()
        self.back_img = pg.transform.scale(img, (width, height))
        self.goal_text = ""
        self.goal_array = []
        self.ar_pos = 0
        self.finish_typing = False

        self.current_pitch = ""

        self.showing = False

        self.talk_source = None

        #sound players for when you talk to person
        #self.game.sound_player.load_sound('high', 'resources/sound/highmur.wav')
        #self.game.sound_player.load_sound('mid', 'resources/sound/midmur.wav')
        #self.game.sound_player.load_sound('deep', 'resources/sound/deepmur.wav')

        #mesures the time you stopped taking with textbox so that you arent stuck in a talking loop(after you finish talking, the person talks again when you clicked to close the textbox)
        self.last_talk = 0
        #time you cant talk again(purely for not getting stuck in a talk loop)
        self.last_talk_time_limit = 200

        self.line_character_limit = 54
        self.char_limit = 54 * 4 - 10

    def play_pitch_sound(self, pitch):
        if not pitch == None:
            self.game.sound_player.play_sound(pitch)

    #check if space bar was clicked
    def event_call(self, event):
        if self.showing:
            if event.key == pg.K_e:
                if self.writing:
                    if self.text == self.goal_text:
                        self.writing = False
                    else:
                        self.finish_typing = True
                else:
                    if self.ar_pos < len(self.goal_array):
                        self.text = ""
                        self.ar_pos += 1
                        self.play_pitch_sound(self.current_pitch)
                        try:
                            self.goal_text = self.goal_array[self.ar_pos]
                        except IndexError:
                            self.writing = False
                            self.showing = False
                            self.game.player.canMove = True
                            self.last_talk = pg.time.get_ticks() #maybe add this to the else part of "if self.ar_pos < len(self.goal_array):"

                            self.talk_source = None
                            return
                        self.writing = True
                    else:
                        self.showing = False
                        self.text = ""
                        self.goal_array = []
                        self.goal_text = ""

                        self.talk_source = None

    #wrap text so its not too long
    def wrap_text(self, text, limit):
        if not text or text == "":
            return ""

        words = text.split()
        lines = []
        current_line = words[0]
        
        for word in words[1:]:
            if len(current_line) + 1 + len(word) <= limit:
                # Add the word to the current line
                current_line += " " + word
            else:
                # Start a new line
                lines.append(current_line)
                current_line = word
        
        # Add the last line
        lines.append(current_line)

        return lines

    #func to start displaying txt
    #call_source is a parameter for the npc that started the conversation
    def display_text(self, text, pitch = None, call_source = None):
        #if text is longer than the character limit, turn it into an array
        if self.writing:
            return False
        
        if not call_source == None:
            self.talk_source = call_source

        #play the correct piteched sound for the character talking
        self.current_pitch = pitch
        self.play_pitch_sound(self.current_pitch)

        if len(text) > self.char_limit:
            #text = text[:self.char_limit]
            text = self.wrap_text(text, self.char_limit)
        else:
            text = [text]

        if type(text) == type("abc"):
            self.goal_text = text
            self.goal_array = []
        else:
            self.goal_array = text
            self.ar_pos = 0
            self.goal_text = self.goal_array[0]

        self.game.player.canMove = False
        self.showing = True
        self.writing = True

    def time_limit_done(self):
        if pg.time.get_ticks() - self.game.text_box.last_talk > self.game.text_box.last_talk_time_limit:
            return True
        return False

    #update the textbox
    def update(self):
        if self.showing:
            if self.writing:
                if self.text == self.goal_text:
                    self.writing = False
                else:
                    if self.finish_typing:
                        self.text = self.goal_text
                        self.finish_typing = False
                        self.writing = False
                    else:
                        if self.game.next_char_event:
                            try:
                                self.text += self.goal_text[len(self.text)]
                            except IndexError:
                                self.writing = False
            else:
                #if sound is playing but textbox not writing, stop playing
                [self.game.sound_player.stop_sound(pit) for pit in ["high", "mid", "deep"] if self.game.sound_player.is_sound_playing(pit)]
            
        else:
            #if sound is playing but textbox not writing, stop playing
            [self.game.sound_player.stop_sound(pit) for pit in ["high", "mid", "deep"] if self.game.sound_player.is_sound_playing(pit)]

    def draw(self):
        if self.showing:
            self.game.screen.blit(self.back_img, self.pos)

            y_ = 15

            for t in self.wrap_text(self.text, self.line_character_limit):
                appliedTxt = self.font.render(t, False, 'black')

                x, y = self.pos

                self.game.screen.blit(appliedTxt, (x + 30, y + y_))

                y_ += 33


###OBJECT RENDERER###  


#object renderer class, for renderering objects, sprites, etc
class ObjectRenderer:
    #def vars and init func
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.wall_textures = self.load_wall_textures()
        self.sky_image = self.get_texture('resources/textures/sky.png', (WIDTH, HALF_HEIGHT))
        self.sky_offset = 0
        #self.blood_screen = pg.transform.scale(pg.image.load('resources/sprites/blood.png'), (WIDTH, HEIGHT)); self.blood_screen.set_alpha(100)
        #self.gameoverImg = 
        self.portal_frames = [self.get_texture('resources/textures/elevator.png')]

        self.portal_frame_n = 0
        self.random_frame_n = 0

        self.popup_list = []

        self.wacky_font = pg.font.Font(None, 20)

        self.y_gap = 10 #gap between popups

        self.popup_d = {}

        self.gameoverImg = pg.transform.scale(pg.image.load("resources/sprites/gameover.png"), (WIDTH, HEIGHT + SHEIGHT))
        self.win_screen = pg.transform.scale(pg.image.load("resources/sprites/winscreen.png"), (WIDTH, HEIGHT + SHEIGHT))

        self.npc_talk_dict = {} #array for all passive npcs to specify if they need the talk text to show or not

        self.needTalk_font = pg.font.Font('resources/textutil/textboxfont.ttf', 30)

    def create_popup(self, txt):
        y = self.next_popup_pos()
        self.popup_list.append(Popup(self.game, txt, y))

    #basically i want to work on something else rn so ill make a makeshift sysmtem, popups append their "last position" and the next popup will be placed a certain amount under the previous message's "last position"
    #the downside of this makeshift system is that if new messages are constantly being created without a moment of no messages, the messages will continually go further and further down because the poss array will always have a value preventing a reset to 0
    def next_popup_pos(self):
        poss = []
        for p in self.popup_list:
            poss.append(p.pos_y + p.surf_y)

        if len(poss) == 0:
            return 0
        else:
            return (poss[-1] + self.y_gap)

    def popup_update(self):
        self.popup_d = {p : p.update() for p in self.popup_list}

    def draw_popups(self):
        for p in self.popup_d:
            self.screen.blit(self.popup_d[p], (10, p.pos_y))

    #function to draw background(sky) and to render all game objects
    def draw(self):
        self.draw_background()
        self.render_game_objects()
        self.draw_popups()

    def draw_npc_talker(self):
        for val in list(self.npc_talk_dict.values()):
            if not val == False:
                needTalk = self.needTalk_font.render("E to talk to " + val[0], False, (255, 255, 255))
                self.game.screen.blit(needTalk, (val[1] - 200, HEIGHT))

    #if you lost, show lose screen
    def game_over(self): self.screen.blit(self.gameoverImg, (0, 0))

    def show_win_screen(self): self.screen.blit(self.win_screen, (0, 0))

    #draw sky and floor, not currently used
    def draw_background(self):
        if not MouseRotation_Setting:
            self.sky_offset = (100 * self.game.player.rel) % WIDTH
        else:
            self.sky_offset = (self.sky_offset + 4.5 * self.game.player.rel) % WIDTH

        self.screen.fill('skyblue')
        
        self.screen.blit(self.sky_image, (-self.sky_offset, 0))
        self.screen.blit(self.sky_image, (-self.sky_offset + WIDTH, 0))
        #floor
        pg.draw.rect(self.screen, FLOOR_COLOR, (0, HALF_HEIGHT, WIDTH, HEIGHT))

    #loop through objects to render, render them
    def render_game_objects(self):
        list_objects = sorted(self.game.raycasting.objects_to_render, key=lambda t: t[0], reverse = True)
        for depth, image, pos in list_objects:
            self.screen.blit(image, pos)

    #a static method to get the texture of a file
    @staticmethod
    def get_texture(path, res=(TEXTURE_SIZE, TEXTURE_SIZE)):
        texture = pg.image.load(path).convert_alpha()
        return pg.transform.scale(texture, res)
    
    #dictionary to store the textures of walls
    def load_wall_textures(self):
        #for every item in the textures dir that ends with .png and whos name is numeric, add it to the directory as a value with its number as its key
        out_dict = {int(pth.replace('.png', '')) : self.get_texture(f'resources/textures/' + pth) for pth in os.listdir('resources/textures') if pth.endswith('.png') and pth.replace('.png', '').isnumeric()}
        out_dict["p"] = self.get_texture('resources/textures/elevator.png')
        return out_dict


###SPRITE OBJECTS###


#class for a sprite, an in game object thats not a wall
class SpriteObject:
    #def vars, init func
    def __init__(self, game, path = 'resources/sprites/static/candlebra.png', 
                 pos=(10.5, 3.5), scale = 0.25, shift = 1.4):
        self.game = game
        self.player = game.player
        self.x, self.y = pos
        self.image = pg.image.load(path).convert_alpha()
        self.IMAGE_WIDTH = self.image.get_width()
        self.IMAGE_HALF_WIDTH = self.image.get_width() // 2
        self.IMAGE_RATIO = self.IMAGE_WIDTH / self.image.get_height()
        self.dx, self.dy, self.theta, self.screen_x, self.dist, self.norm_dist = 0,0,0,0,1,1
        self.sprite_half_width = 0
        self.SPRITE_SCALE = scale
        self.SPRITE_HEIGHT_SHIFT = shift
        self.img_angle = 0

    #mesure the sprite's projections, add itself to objects to render with its normalized distance, actual image and position
    def get_sprite_projection(self):
        proj = SCREEN_DIST / self.norm_dist * self.SPRITE_SCALE
        proj_width, proj_height = proj * self.IMAGE_RATIO, proj
        

        image = pg.transform.scale(self.image, (proj_width, proj_height))

        if not self.img_angle == 0:
            image = rotate_image(image, self.img_angle)

        self.sprite_half_width = proj_width // 2
        height_shift = proj_height * self.SPRITE_HEIGHT_SHIFT
        pos = self.screen_x - self.sprite_half_width, HALF_HEIGHT - proj_height //2 + height_shift

        self.game.raycasting.objects_to_render.append((self.norm_dist, image, pos))

    #function to get sprite
    def get_sprite(self):
        dx = self.x - self.player.x
        dy = self.y - self.player.y
        self.dx, self.dy = dx, dy
        self.theta = math.atan2(dy, dx)

        delta = self.theta - self.player.angle
        if (dx > 0 and self.player.angle > math.pi) or (dx < 0 and dy < 0):
            delta += math.tau

        delta_rays = delta / DELTA_ANGLE
        self.screen_x = (HALF_NUM_RAYS + delta_rays) * SCALE

        self.dist = math.hypot(dx, dy)
        self.norm_dist = self.dist * math.cos(delta)
        if -self.IMAGE_HALF_WIDTH < self.screen_x < (WIDTH + self.IMAGE_HALF_WIDTH) and self.norm_dist > 0.5:
            self.get_sprite_projection()

    def self_destruct(self):
        self.game.object_handler.sprite_list.remove(self)
        del self

    #update sprite
    def update(self):
        self.get_sprite()

class Pickup(SpriteObject):
    #type would be item/money/special/etc, subtype would really be for special type, number is for the number of the thing you pickup, subtype will be the id of item if the type is item
    def __init__(self, game, pos, type, path=None, number=1, scale=0.25, shift=1.6, subtype = ""):
        if path == None and type == 'item':
            #its purposefully game and not self.game because super is called after and game is the same and this needs to be before super init
            path = game.inventory_system.get_item_by_id(subtype).icon
        super().__init__(game, path, pos, scale, shift)
        self.type = type
        self.subtype = subtype
        self.number = number
        self.pickup_range = 1

    def in_player_range(self):
        sx, sy = self.x, self.y
        px, py = self.game.player.map_pos
        return distance_formula(sx, sy, px, py) <= self.pickup_range
    
    def self_destruct(self):
        self.game.object_handler.pickup_list.remove(self)
        del self

    def update_sub(self):
        removed = False
        if self.in_player_range():
            if self.type == "money":
                pass

            elif self.type == "sus":
                self.game.player.raise_suspicion(-3)
                self.game.object_renderer.create_popup(f"Disguise lowered your suspicion level by 3")
                removed = True

            elif self.type == "item":
                self.game.inventory_system.add_item(self.game.inventory_system.get_item_by_id(self.subtype), self.number)
                self.game.object_renderer.create_popup(f"Gained {str(self.number)} {self.game.inventory_system.get_item_by_id(self.subtype).name}'s")
                self.game.sound_player.play_sound("pickup", loop=False)
                removed = True

            elif self.type == "special":
                #if self.subtype == "stomachmedicine":
                    #self.game.inventory_system.add_item(self.game.inventory_system.get_item_by_id(1))
                    #self.game.object_renderer.create_popup("Gained stomach medicine")
                    #self.game.sound_player.play_sound("pickup", loop=False)
                    #removed = True
                pass

                #else:
                    #raise ValueError(self.subtype + "is an invalid pickup subtype")
                
            else:
                raise ValueError(self.type + " is an invalid pickup type")
            
        if removed:
            self.game.object_handler.disable_pickup(self)
            del self
            
class BasicPassiveNPC(SpriteObject):
    def __init__(self, game, path='resources/sprites/passive/ghost.png', pos=(10.5, 3.5), usetextbox=True, myline="hello", 
                 name="character", pitch="high", scale=0.75, shift=0, special_tag = None): #pitch: high/mid/deep
        super().__init__(game, path, pos, scale, shift)
        self.talkrange = 2.5
        self.pos = pos
        #trigger text box for his line or just make text float above him
        self.use_textbox = usetextbox
        self.myline = myline
        self.myname = name
        self.pitch = pitch
        self.interact_enabled = True
        self.special_tag = special_tag

        self.exclamation = False

        self.nextlinequery = []

        self.dont_show_textbox = None #var to not show textbox after special_check()

    #SPECIAL FUNCTION#
    def close_pawn_shop(self):
        if len(self.nextlinequery) == 0:
            self.game.text_box.display_text(self.myline, self.pitch, call_source=self)
        else:
            self.game.text_box.display_text(self.nextlinequery[0], self.pitch, call_source=self); self.nextlinequery.pop(0)
        self.dont_show_textbox = None
    #/SPECIAL FUNCTIONS#


    def player_in_range(self):
        sx, sy = self.pos
        px, py = self.game.player.map_pos
        return distance_formula(sx, sy, px, py) <= self.talkrange

    #NEED TO ADD AN EXCLAMATION AND A FUNC TO ASK PASSIVES FOR THEIR NEXT TALK

    def event_call(self, event):
        if self.player_in_range() and self.interact_enabled:
            if event.key == pg.K_e and not self.game.text_box.showing and self.game.text_box.time_limit_done() and self.use_textbox and not self.game.display_menu.showing: #maybe add a self.screen_x req so that you cant talk to people behind you
                self.special_check()

                if self.dont_show_textbox == True:
                    return
                if len(self.nextlinequery) == 0:
                    self.game.text_box.display_text(self.myline, self.pitch, call_source=self)
                else:
                    self.game.text_box.display_text(self.nextlinequery[0], self.pitch, call_source=self)
                    self.nextlinequery.pop(0)

    def update_sub(self):
        pass

        #if within range, allow talk
        if self.player_in_range() and self.interact_enabled:
            if not self.game.text_box.showing:
                self.game.object_renderer.npc_talk_dict[self] = [self.myname, self.screen_x]
            else:
                self.game.object_renderer.npc_talk_dict[self] = False
        else:
            self.game.object_renderer.npc_talk_dict[self] = False
            
    def special_check(self): #maybe make another one for special checks in update for some cases
        #place to special things for special tags
        if not self.special_tag == None:
            pass

    def add_next_line(self, line):
        self.nextlinequery.append(line)

    def self_destruct(self):
        self.game.object_handler.passive_list.remove(self)
        del self


#a class piggybacking off the spriteobject that contains animation
class AnimatedSprite(SpriteObject):
    def __init__(self, game, path='resources/sprites/static/johny.png', pos=(10.5, 3.5), scale=1, shift=0.27, animation_time=120):
        super().__init__(game, path, pos, scale, shift)
        self.animation_time = animation_time
        self.path = path.rsplit('/', 1)[0]
        self.images = self.get_images(self.path)
        self.animation_time_prev = pg.time.get_ticks()
        self.animation_trigger = False

    #update itself
    def update(self):
        super().update()
        self.check_animation_time()
        self.animate(self.images)

    #function to play animation
    def animate(self, images):
        if self.animation_trigger:
            images.rotate(-1)
            self.image = images[0]

    #function to check the animation's time and change the animation trigger
    def check_animation_time(self):
        self.animation_trigger = False
        time_now = pg.time.get_ticks()
        if time_now - self.animation_time_prev > self.animation_time:
            self.animation_time_prev = time_now
            self.animation_trigger = True

    #function to get all the images in a folder for animating
    def get_images(self, path):
        #func to sort an array of image paths(i.e. 0.png, 1.png, etc) by their first number to prevent os from ordering them wrong
        def spec_sort(ar):
            try:
                return [x for _, x in sorted(zip([int(val.replace('.png', '')) for val in ar], ar))]
            except ValueError:
                return ar

        images = deque()

        searchpath = spec_sort(os.listdir(path))

        for file_name in searchpath:
            if os.path.isfile(os.path.join(path, file_name)):
                img = pg.image.load(path + "/" + file_name).convert_alpha()
                images.append(img)
        return images


###OBJECT HANDLER###


#object handler class, basically manages objects and some interactions/functions
class ObjectHandler:
    def __init__(self, game):
        self.game = game
        self.sprite_list = []
        self.npc_list = []
        self.passive_list = []
        self.pickup_list = []

        self.npc_sprite_path = 'resources/sprites/npc'
        self.static_sprite_path = 'resources/sprites/static/'
        self.anim_sprite_path = 'resources/sprites/animated'

        #dictionary of npc positions
        self.npc_positions = {}

        #dictionary of basicpassivenpcs' and how centered they are, the more center the more priority for talking to him
        self.passive_centered = {}

        self.hut_boss = None
        self.boss = None

        if not self.game.map.need_to_load == None:
            self.load_level_spawns(self.game.map.need_to_load)
            self.game.map.need_to_load = None    

    #update all individual sprites and npcs
    def update(self):
        self.npc_positions = {npc.map_pos for npc in self.npc_list if npc.alive}

        #creates a dict of the passive npcs and their "centeredness"
        self.passive_centered = {passive : abs(passive.screen_x - HALF_WIDTH) for passive in self.passive_list if passive.player_in_range()}

        #if there is one passive npc on the screen and in range of the player, only allow the player to talk to him
        if len(self.passive_centered) == 1:
            list(self.passive_centered.keys())[0].interact_enabled = True
        #if there is more than one passive npcs on the screen/in range, only allow the most centered one of them all to talk to the player
        elif len(self.passive_centered) > 1:
            self.passive_centered = dict(sorted(self.passive_centered.items(), key=lambda x: int(x[1])))
            passive_keys = list(self.passive_centered.keys())
            passive_keysl = len(passive_keys)
            passive_keys[0].interact_enabled = True
            for x in range(1, passive_keysl):
                passive_keys[x].interact_enabled = False

        [sprite.update() for sprite in self.sprite_list]
        [npc.update() for npc in self.npc_list]
        [passive.update() for passive in self.passive_list]; [passive.update_sub() for passive in self.passive_list]
        [pickup.update() for pickup in self.pickup_list]; [pickup.update_sub() for pickup in self.pickup_list]

        if not len(self.game.object_renderer.npc_talk_dict) == len(self.passive_list):
            self.game.object_renderer.npc_talk_dict = {n : False for n in self.passive_list}

        #go through every sprite and if it has the update_sub function, run it (This will be used for subclasses that have extra abilities that will all be run with update_sub)
        [sprite.update_sub() for sprite in self.sprite_list if callable(getattr(sprite, "update_sub", None))]

        

    def clear_entities(self):
        arl = len(self.sprite_list)
        for x in range(arl):
            self.sprite_list[0].self_destruct()

        arl = len(self.npc_list)
        for x in range(arl):
            self.npc_list[0].self_destruct()

        arl = len(self.passive_list)
        for x in range(arl):
            self.passive_list[0].self_destruct()

        arl = len(self.pickup_list)
        for x in range(arl):
            self.pickup_list[0].self_destruct()

    def load_level_spawns(self, spawndict):
        self.clear_entities()

        if "npc" in spawndict:
            npcar = spawndict["npc"]

            for npc in npcar:
                npctype = npc[0]
                npcspawn = npc[1][0], npc[1][1]
                
                enemy_data = ENEMIES[npctype]

                self.add_npc(NPC(self.game, enemy_data["path"], npcspawn, enemy_data["scale"], enemy_data["shift"], enemy_data["animation_time"], enemy_data["stats"], none_get(enemy_data, "drops")))

        if "passive" in spawndict:
            passar = spawndict["passive"]

            for passive in passar:
                self.add_passive(BasicPassiveNPC(self.game, passive["path"], (passive["pos"][0], passive["pos"][1]), passive["usetextbox"], passive["myline"], 
                                                 passive["name"], passive["pitch"], passive["scale"], passive["shift"], passive["special_tag"]))

        if "sprites" in spawndict:
            spritar = spawndict["sprites"]

            for sprit in spritar:
                self.add_sprite(SpriteObject(self.game, sprit[0], (sprit[1][0], sprit[1][1]), sprit[2], sprit[3]))

        if "pickups" in spawndict:
            print("a")
            pickar = spawndict["pickups"]

            for pick in pickar:
                self.add_pickup(Pickup(self.game, (pick[0][0], pick[0][1]), pick[1], pick[2], pick[3], pick[4], pick[5], pick[6]))

    #function to add an npc
    def add_npc(self, npc):
        self.npc_list.append(npc)
    def damage_all_npc_in_range(self, x, y, range, dmg):
        for _npc in self.npc_list:
            nx, ny = _npc.map_pos
            if distance_formula(x, y, nx, ny) < range:
                _npc.get_damaged(dmg)

    #function to create a static sprite
    def add_sprite(self, sprite):
        self.sprite_list.append(sprite)

    def add_passive(self, passive):
        self.passive_list.append(passive)
    def get_special_passive(self, special_tag): #func to get the passive npc with the correct special tag
        for passive in self.passive_list:
            if passive.special_tag == special_tag:
                return passive
        return None

    def add_pickup(self, pickup):
        self.pickup_list.append(pickup)
    def disable_pickup(self, pickup):
        self.pickup_list.remove(pickup)

    def npc_on_square(self, coord):
        for npc in self.npc_list:
            nx, ny = npc.x, npc.y
            cx, cy = coord
            if distance_formula(nx, ny, cx, cy) <= 1.25:
                return npc


###SOUND###


#sound function, inits the pygame mixer and holds the sounds
class Sound:
    def __init__(self, game):
        self.game = game
        pg.mixer.init()
        self.path = 'resources/sound/'

class SoundPlayer:
    def __init__(self):
        pg.mixer.init()
        self.sounds = {}

        self.load_sound('disguise', 'resources/sound/disguise.mp3')
        self.load_sound('alert', 'resources/sound/alert.mp3')
        self.load_sound('vineboom', 'resources/sound/vineboom.mp3')
        self.load_sound('theme', 'resources/sound/infiltheme.wav')

    def load_sound(self, sound_name, sound_file_path):
        self.sounds[sound_name] = pg.mixer.Sound(sound_file_path)

    def play_sound(self, sound_name, volume=None, loop=True):
        if sound_name in self.sounds:
            sound = self.sounds[sound_name]
            if volume is not None:
                sound.set_volume(volume)
            sound.play(loops=-1 if loop else 0)

    def stop_sound(self, sound_name):
        if sound_name in self.sounds:
            self.sounds[sound_name].stop()

    def is_sound_playing(self, sound_name):
        if sound_name in self.sounds:
            try:
                return self.sounds[sound_name].get_num_channels() > 0
            except pg.error:
                return False
        return False


###NPC###


#non player character class, manages its npc's interaction/movement/work and its graphics
class NPC(AnimatedSprite):
    def __init__(self, game, path='resources/sprites/npc/basic/0.png', pos=(10.5, 5.5), scale = 0.6, shift = 0.38, animation_time=180, stats = None, drops = None, life_bond = None): #stats is an optional stats class that defines the enemy's stats
        super().__init__(game, path, pos, scale, shift, animation_time)

        self.current_atk = None

        self.random_engine = None

        if stats == None:
            self.vision_dist = 2
            self.suspicion_lvl = 0.03
            self.speed = 1
            self.size = 100
        else:
            self.vision_dist = stats.vision_dist
            self.suspicion_lvl = stats.suspicion_lvl
            self.speed = stats.speed
            self.size = stats.size
            self.follower = stats.follower
            self.minsus = stats.minsus
            if stats.random_walk:
                self.random_engine = NPCRandomMovement(self.game, self, self.movement)

        self.alive = True

        #gets all its animations's frame
        self.idle_images = None
        self.walk_images = None
        if os.path.exists(self.path + '/idle'):
            self.idle_images = self.get_images(self.path + '/idle')
        if os.path.exists(self.path + '/walk'):
            self.walk_images = self.get_images(self.path + '/walk')

        self.ray_cast_value = False
        self.frame_counter = 0

        #1. the time this npc died, 2.time before the npc will delete himself - if time_now - time_died > time_before_del: delete himself
        self.time_died = 0
        self.time_before_del = 5000

        #trigger to use pathfinding to hunt player down
        self.player_search_trigger = False

        self.drops = drops

        self.genStealth = False

        self.bond_npc = None if life_bond == None else life_bond

    def self_destruct(self):
        self.game.object_handler.npc_list.remove(self)
        del self

    #update npc
    def update(self):
        if self.random_engine != None and not self.player_search_trigger:
            self.random_engine.update()

        self.check_animation_time()
        self.get_sprite()
        self.run_logic()

    #check if location is wall
    def check_wall(self, x, y):
        return (x, y) not in self.game.map.world_map
    
    #check if potential movement goes into wall
    def check_wall_collision(self, dx, dy):
        if self.check_wall(int(self.x + dx * self.size), int(self.y)):
            self.x += dx
        if self.check_wall(int(self.x), int(self.y + dy * self.size)):
            self.y += dy

    #manage all npc movement
    def movement(self, nonplayer = False, otherCoord = (None, None)): #nonplayer is for when the npc isnt trying to go to the player but rather somewhere else(otherCoord)
        if nonplayer:
            #use pathfinding algo to find next location
            next_pos = self.game.pathfinding.get_path(self.map_pos, otherCoord)
            next_x, next_y = next_pos

            #dont move there if there is already an npc standing in that square
            if next_pos not in self.game.object_handler.npc_positions:
                #mesure angle torward player and mesure potential movement
                angle = math.atan2(next_y + 0.5 - self.y, next_x + 0.5 - self.x)
                dx = math.cos(angle) * self.speed
                dy = math.sin(angle) * self.speed
                self.check_wall_collision(dx, dy)

        #use pathfinding algo to find next location
        next_pos = self.game.pathfinding.get_path(self.map_pos, self.game.player.map_pos)
        next_x, next_y = next_pos

        #dont move there if there is already an npc standing in that square
        if next_pos not in self.game.object_handler.npc_positions:
            #mesure angle torward player and mesure potential movement
            angle = math.atan2(next_y + 0.5 - self.y, next_x + 0.5 - self.x)
            dx = math.cos(angle) * self.speed
            dy = math.sin(angle) * self.speed
            self.check_wall_collision(dx, dy)

    #main logic runner for npc
    def run_logic(self):
        if self.alive:
            if self.bond_npc != None:
                pass

            #check if there is a clear line of sight between player and npc
            self.ray_cast_value = self.ray_cast_player_npc() 

            if self.game.player.stealth >= self.minsus and distance_formula(self.x, self.y, self.player.x, self.player.y) <= self.vision_dist or self.game.player.criminal_stealth:
                self.player_search_trigger = True
                if 'goku' in self.path:
                    self.game.sound_player.play_sound("vineboom", loop = False)
                else:
                    self.game.sound_player.play_sound("alert", loop = False)
            else:
                if self.player_search_trigger == True and not self.ray_cast_value and not distance_formula(self.x, self.y, self.player.x, self.player.y) <= self.vision_dist:
                    self.player_search_trigger = False

            #if saw player, start hunting him down and moving torwards him, starts pathfinding algo
            if self.ray_cast_value and self.follower or (not self.genStealth and self.ray_cast_value and distance_formula(self.x, self.y, self.player.x, self.player.y) <= self.vision_dist):
                if not self.genStealth:
                    self.genStealth = True
                    self.game.player.raise_suspicion(self.suspicion_lvl)

            elif self.player_search_trigger: #add 'or' for adding an option for follow if stealth too high
                if not self.walk_images == None:
                    self.animate(self.walk_images)
                self.movement()

            else:
                if self.idle_images != None:
                    self.animate(self.idle_images)
        else:
            self.animate_death()

    #class property of position on map
    @property
    def map_pos(self):
        return int(self.x), int(self.y)
    
    #check if there is a clear line of sight b/w player and npc using raycasting similar to the players one
    def ray_cast_player_npc(self):
        if self.game.player.map_pos == self.map_pos:
            return True
        
        wall_dist_v, wall_dist_h = 0, 0
        player_dist_v, player_dist_h = 0, 0

        ox, oy = self.game.player.pos
        x_map, y_map = self.game.player.map_pos

        ray_angle = self.theta
        sin_a = math.sin(ray_angle)
        cos_a = math.cos(ray_angle)

        #horizontals
        y_hor, dy = (y_map + 1, 1) if sin_a > 0 else (y_map - 1e-6, -1)

        depth_hor = (y_hor - oy) / sin_a
        x_hor = ox + depth_hor * cos_a

        delta_depth = dy / sin_a
        dx = delta_depth * cos_a

        for i in range(MAX_DEPTH):
            tile_hor = int(x_hor), int(y_hor)
            if tile_hor == self.map_pos:
                player_dist_h = depth_hor
                break
            if tile_hor in self.game.map.world_map:
                wall_dist_h = depth_hor
                break
            x_hor += dx
            y_hor += dy
            depth_hor += delta_depth

        #verticals
        x_vert, dx = (x_map + 1, 1) if cos_a > 0 else (x_map - 1e-6, -1)

        depth_vert = (x_vert - ox) / cos_a
        y_vert = oy + depth_vert * sin_a

        delta_depth = dx / cos_a
        dy = delta_depth * sin_a

        for i in range(MAX_DEPTH):
            tile_vert = int(x_vert), int(y_vert)
            if tile_vert == self.map_pos:
                player_dist_v = depth_vert
                break
            if tile_vert in self.game.map.world_map:
                wall_dist_v = depth_vert
                break
            x_vert += dx
            y_vert += dy
            depth_vert += delta_depth

        player_dist = max(player_dist_h, player_dist_v)
        wall_dist = max(wall_dist_h, wall_dist_v)

        #if there is a clear line of sight between player and enemy
        if 0 < player_dist < wall_dist or not wall_dist:
            return True
        return False

class NPCRandomMovement():
    def __init__(self, game, npc, move):
        self.game = game
        self.npc = npc
        self.move = move

        self.time_between_moves = randint(2000, 9000)
        self.time_from_last_move = 0

        self.goal = self.get_goal()

        self.walking = False

    def update(self):
        if pg.time.get_ticks() - self.time_from_last_move >= self.time_between_moves and not self.walking:
            self.goal = self.get_goal()
            self.walking = True
        elif self.walking:
            self.move(nonplayer = True, otherCoord = self.game.pathfinding.get_path(self.npc.map_pos, self.goal))
            gx, gy = self.goal
            if distance_formula(self.npc.x, self.npc.y, gx, gy) <= 1:
                self.walking = False
                self.time_from_last_move = pg.time.get_ticks()
                self.time_between_moves = randint(2000, 9000)

    def get_goal(self):
        return choice(self.game.pathfinding.free_cords)

        
###PATHFINDING ###


#pathfind class, uses simple pathfinding algo for all npcs to use
class PathFinding:
    def __init__(self, game):
        self.game = game
        self.map = game.map.cur_map
        self.ways = [-1, 0], [0, -1], [1, 0], [0, 1], [-1, -1], [1, -1], [1, 1], [-1, 1]
        self.graph = {}
        self.get_graph()
        self.free_cords = []
        self.get_free_cords()

    def reset_pathfinding(self, newmap):
        self.map = newmap
        self.graph = {}
        self.get_graph()
        self.free_cords = []
        self.get_free_cords()

    #main function, returns the next square to move to, to optimally reach goal from start
    def get_path(self, start, goal):
        #creates collection of already visited squares
        self.visited = self.bfs(start, goal, self.graph)

        if self.visited == None:
            return start

        path = [goal]
        step = self.visited.get(goal, start)

        #while not reached goal continue
        while step and step != start:
            path.append(step)
            step = self.visited[step]
        return path[-1]

    #pathfinding algo
    def bfs(self, start, goal, graph):
        queue = deque([start])
        visited = {start: None}

        while queue:
            cur_node = queue.popleft()
            if cur_node == goal:
                break

            try:
                next_nodes = graph[cur_node]
            except KeyError:
                print("WARNING: There has been a keyerror in pathfinding, KEYERROR conjured by: " + str(cur_node))
                return None

            for next_node in next_nodes:
                if next_node not in visited and next_node not in self.game.object_handler.npc_positions:
                    queue.append(next_node)
                    visited[next_node] = cur_node
        return visited

    #returns nearby nodes
    def get_next_nodes(self, x, y):
        return [(x + dx, y + dy) for dx, dy in self.ways if (x + dx, y + dy) not in self.game.map.world_map]

    #something
    def get_graph(self):
        for y, row in enumerate(self.map):
            for x, col in enumerate(row):
                if not col:
                    self.graph[(x, y)] = self.graph.get((x, y), []) + self.get_next_nodes(x, y)

    def get_free_cords(self):
        for y, row in enumerate(self.map):
            for x, col in enumerate(row):
                if not col:
                    self.free_cords.append((x, y))


###DISPLAY MENU###


DISPLAY_RES = DISPLAY_X, DISPLAY_Y = 600, 450
SLOT_SIZE = SLOT_X, SLOT_Y = 75, 75

#class for inventory icons, creates one per item in inventory
class InventoryIcon:
    def __init__(self, game, id, from_pawn_shop = False):
        self.game = game
        self.id = id
        self.icon = ""
        self.quantity = 0
        self.from_pawn_shop = from_pawn_shop

        self.posx, self.posy = None, None

        if from_pawn_shop:
            self.darken = False
    
    def update_id(self, id):
        self.id = id

    def set_pos(self, x, y):
        self.posx = x; self.posy = y

    def update(self):
        #function to update self.icon and self.quantity to the position of self.id in the inventory
        if self.from_pawn_shop:
            myitem = self.game.pawn_shop.item_list[self.id]
        else:
            myitem = self.game.display_menu.item_list[self.id]
        self.icon = myitem.icon
        self.quantity = self.game.inventory_system.inventory[myitem]

        return self.draw()

    def lighten_slot(self):
        if self.from_pawn_shop:
            self.darken = False

    def darken_slot(self):
        if self.from_pawn_shop:
            self.darken = True

    def draw(self):
        my_surface = pg.Surface(SLOT_SIZE)

        white_bck = pg.Rect(3, 3, SLOT_X - 6, SLOT_Y - 6)
        pg.draw.rect(my_surface, (255, 255, 255), white_bck)

        icon_img = pg.image.load(self.icon)

        icon_img = pg.transform.scale(icon_img, (SLOT_X - 6, SLOT_Y - 6))

        wacky_font = pg.font.Font('resources/textutil/wackyfont.ttf', 25)

        if self.quantity > 1:
            quantity_txt = wacky_font.render(str(self.quantity), False, (0, 0, 0))

        my_surface.blit(icon_img, (2, 3))
        if self.quantity > 1:
            my_surface.blit(quantity_txt, (SLOT_X - quantity_txt.get_width() - 5, SLOT_Y - quantity_txt.get_height())) ##NEED TO FIX QUANTITY TEXT

        if self.from_pawn_shop:
            if self.darken:
                s = pg.Surface(SLOT_SIZE); s.set_alpha(128); s.fill((0, 0, 0))
                my_surface.blit(s, (0,0))

        #return a finished icon surface

        return my_surface

    def check_mouse_click(self, mx, my):
        if self.posx == None or self.posy == None:
            return
    
        if (self.posx <= mx <= self.posx + SLOT_X) and (self.posy <= my <= self.posy + SLOT_Y):
            self.game.pawn_shop.slot_clicked(self)

#class for showing inventory
SLOT_HOR_LIMIT = 6

class DisplayMenu:
    def __init__(self, game):
        self.game = game

        self.screen = self.game.screen

        self.showing = False

        self.item_list = []
        self.inventory_icons = []

        self.inven_surface = None

        self.wacky_font = pg.font.Font(None, 30)

    def draw(self):
        if self.showing:
            self.inven_surface = pg.Surface(DISPLAY_RES)

            pg.draw.rect(self.inven_surface, 'white', (5, 5, DISPLAY_X - 10, DISPLAY_Y - 10))

            self.inven_surface.set_alpha(210)

            self.draw_inventory()

            self.screen.blit(self.inven_surface, (80, 80))

    def event_call(self, event):
        if event.key == pg.K_TAB and not self.game.text_box.showing:
            self.showing = not self.showing
            if self.showing:
                self.game.setMouseVisibility(True)
            else:
                self.game.setMouseVisibility(False)

    def draw_inventory(self):
        self.item_list = []
        for itm in self.game.inventory_system.inventory:
            self.item_list.append(itm)

        missing_icon_n = len(self.item_list) - len(self.inventory_icons)

        if missing_icon_n > 0:
            for x in range(missing_icon_n):
                self.inventory_icons.append(InventoryIcon(self.game, len(self.inventory_icons)))
        elif missing_icon_n < 0:
            for x in range(abs(missing_icon_n)):
                self.inventory_icons.pop(-1)

            n = 0
            for icon in self.inventory_icons:
                icon.update_id(n)
                n+=1

        pos = 0
        for icon in self.inventory_icons:
            slot = icon.update()

            x_padding, y_padding = 10, 10

            self.inven_surface.blit(slot, ((pos % SLOT_HOR_LIMIT) * SLOT_X + x_padding * pos + 30, (math.floor(pos / SLOT_HOR_LIMIT)) * SLOT_Y + y_padding * math.floor(pos / SLOT_HOR_LIMIT) + 30))

            pos+=1

    def update(self):
        if self.showing:
            self.game.player.inventoryOpen = True
        else:
            self.game.player.inventoryOpen = False

class PawnShopMenu:
    def __init__(self, game):
        self.game = game

        self.screen = self.game.screen

        self.showing = True

        self.item_list = []
        self.inventory_icons = []

        self.inven_surface = None

        self.selected_slot = None

        self.mouseX, self.mouseY = 0, 0

        self.screen = self.game.screen

        self.show_counter = True

        self.counter = 0

        self.font = pg.font.Font(None, 60)
        self.smallfont = pg.font.Font(None, 40)

        self.price_counter = self.font.render("0$", False, (0, 0, 0))
        self.sell_array = [] #cansell bool, price to get

        self.counter_surf = pg.Surface((60, 60))

        self.buttons = []

        self.buttons.append(MenuButton(self, (1500, 50), 50, 50, "X", self.close_shop))

        self.buttons.append(MenuButton(self, (975, 160), 100, 50, "5", self.plus_five))
        self.buttons.append(MenuButton(self, (975, 215), 100, 50, "10", self.plus_ten))
        self.buttons.append(MenuButton(self, (975, 270), 100, 50, "All", self.max_counter))

        self.buttons.append(MenuButton(self, (1060, 420), 30, 40, ">", self.plus_one))
        self.buttons.append(MenuButton(self, (960, 420), 30, 40, "<", self.minus_one))

        self.buttons.append(MenuButton(self, (975, 525), 100, 50, "Sell", self.sell_button))

        self.set_showing(False)
        self.redraw_counter()
        self.show_images(False)

    def sell_button(self):
        if self.sell_array[0]:
            self.game.inventory_system.remove_item(self.item_list[self.selected_slot.id], self.counter)
            self.game.inventory_system.add_item(self.game.inventory_system.get_item_by_id(2), self.sell_array[1])
            self.selected_slot.lighten_slot()
            self.selected_slot = None
            self.counter = 0
            self.update_counter()
            self.show_images(False, closeX=False)
            return

    def close_shop(self):
        self.set_showing(False)
        self.game.setMouseVisibility(False)
        self.game.object_handler.get_special_passive("pawndonkey").close_pawn_shop()

    def redraw_counter(self):
        self.counter_surf.fill('black')
        pg.draw.rect(self.counter_surf, 'lightgray', (3, 3, 54, 54))
        count_txt = self.font.render(str(self.counter), False, (0, 0, 0))
        self.counter_surf.blit(count_txt, (60//2 - count_txt.get_width()//2, 60//2 - count_txt.get_height()//2))

        if self.selected_slot == None:
            self.price_counter = None
            return

        item = self.item_list[self.selected_slot.id]

        try:
            tprice = self.counter * PAWN_PRICES[item.id]
        except KeyError:
            self.price_counter = self.smallfont.render("CAN'T SELL", False, (255, 255, 255))
            self.sell_array = [False]
            return

        self.price_counter = self.font.render(str(tprice) + "$", False, (0, 0, 0))
        self.sell_array = [True, tprice]

    def update_counter(self):
        if self.selected_slot == None:
            self.counter = 0
            self.redraw_counter()
            return

        maxquan = self.game.inventory_system.inventory[self.item_list[self.selected_slot.id]] #gets the id from the selected slot, gets the item of that slot, gets the quantity from the inventory using the slot item
        if self.counter > maxquan:
            self.counter = maxquan
        if self.counter < 1:
            self.counter = 1

        self.redraw_counter()

        self.buttons[-1].lock_color_change = not self.sell_array[0]

    def max_counter(self):
        self.counter += 99999
        self.update_counter()

    def plus_ten(self):
        self.counter += 10
        self.update_counter()

    def plus_five(self):
        self.counter += 5
        self.update_counter()

    def minus_one(self):
        self.counter -= 1
        self.update_counter()

    def plus_one(self):
        self.counter += 1
        self.update_counter()

    def set_showing(self, shw):
        if shw:
            self.game.setMouseVisibility(True)

        self.showing = shw
        self.show_images(False, closeX=False)

    def show_images(self, shw, closeX = True):
        self.show_counter = shw
        [but.changeHidden(not shw) for but in self.buttons]

        if not closeX:
            for but in self.buttons:
                if but.functionToCall == self.close_shop:
                    but.changeHidden(False)

    def update_mouse(self):
        self.mouseX, self.mouseY = pg.mouse.get_pos()
        self.mouseX *= RatioWidth
        self.mouseY *= RatioHeight * 1.22

    def draw(self):
        if self.showing:
            self.inven_surface = pg.Surface(DISPLAY_RES)

            pg.draw.rect(self.inven_surface, 'white', (5, 5, DISPLAY_X - 10, DISPLAY_Y - 10))

            self.inven_surface.set_alpha(240)

            self.update_mouse()

            self.draw_inventory()

            if self.show_counter:
                self.screen.blit(self.counter_surf, (995, 415))
                if self.price_counter != None:
                    self.screen.blit(self.price_counter, (960, 485))

            [but.update() for but in self.buttons]
            [but.draw() for but in self.buttons]

            self.screen.blit(self.inven_surface, (350, 150))

    def draw_inventory(self):
        self.item_list = []
        for itm in self.game.inventory_system.inventory:
            self.item_list.append(itm)

        missing_icon_n = len(self.item_list) - len(self.inventory_icons)

        if missing_icon_n > 0:
            for x in range(missing_icon_n):
                self.inventory_icons.append(InventoryIcon(self.game, len(self.inventory_icons), True))
        elif missing_icon_n < 0:
            for x in range(abs(missing_icon_n)):
                self.inventory_icons.pop(-1)

            n = 0
            for icon in self.inventory_icons:
                icon.update_id(n)
                n+=1

        pos = 0
        for icon in self.inventory_icons:
            slot = icon.update()

            x_padding, y_padding = 10, 10

            x = (pos % SLOT_HOR_LIMIT) * SLOT_X + x_padding * pos + 30
            y = (math.floor(pos / SLOT_HOR_LIMIT)) * SLOT_Y + y_padding * math.floor(pos / SLOT_HOR_LIMIT) + 30

            self.inven_surface.blit(slot, (x, y))

            icon.set_pos(x + 350, y + 150) #adding 350 and 150 from "self.screen.blit(self.inven_surface, (350, 150))" because x and y is mesured relative to the inventory, adding padding makes it relative to the whole screen

            pos+=1

    def slot_clicked(self, slot):
        if self.selected_slot == slot:
            slot.lighten_slot()
            self.selected_slot = None
            self.counter = 0
            self.update_counter()
            self.show_images(False, closeX=False)
            return
        elif self.selected_slot != slot and self.selected_slot != None:
            self.selected_slot.lighten_slot()
            self.selected_slot = slot
            self.selected_slot.darken_slot()
        elif self.selected_slot != slot and self.selected_slot == None:
            self.selected_slot = slot
            slot.darken_slot()
        self.update_counter()
        self.show_images(True)

    def check_slot_click(self):
        if not self.showing:
            return

        [i.check_mouse_click(self.mouseX, self.mouseY) for i in self.inventory_icons]
        [but.mouseClick() for but in self.buttons]


###POPUP MESSAGE###


class Popup:
    def __init__(self, game, msg, y):
        self.game = game
        self.text = msg
        self.fade = 255
        self.pos_y = y
        #need to scale the y-axis using the number of chars and some formula
        self.surf_y = 15 + 15 * len(self.game.text_box.wrap_text(self.text, 34))#mesure the y coordinates

        self.mysurface = pg.Surface((250, self.surf_y))

        self.create()

    def create(self):
        pg.draw.rect(self.mysurface, 'white', (0, 0, 250, self.surf_y), border_radius=4)

        y_cor = 10

        for txt in self.game.text_box.wrap_text(self.text, 34):
            self.mysurface.blit(self.game.object_renderer.wacky_font.render(txt, False, (0, 0, 0)), (10, y_cor))
            y_cor += 15

        #self.mysurface.set_alpha(self.fade)
    
    def update(self):
        self.fade -= 1
        if self.fade <= 0:
            self.self_destruct()
        #self.mysurface.set_alpha(self.fade) #IF YOU ENABLE THIS, this will enable popup messages to FADE OUT!!
        return self.mysurface

    def self_destruct(self):
        self.game.object_renderer.popup_list.remove(self)
        del self
        return


###CROSSBAR###

###STATBAR###

class StatBar:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.wacky_font = pg.font.Font('resources/textutil/wackyfont.ttf', 80)

    def draw(self):
        #pg.draw.rect(self.screen, FLOOR_COLOR, (0, HALF_HEIGHT, WIDTH, HEIGHT))
        pg.draw.rect(self.screen, 'black', (0, HEIGHT, WIDTH, SHEIGHT))

        wacky_font = self.wacky_font

        sus = wacky_font.render("Suspicion: " + str(self.game.player.stealth), False, SUSFONT_COLOR)
        self.screen.blit(sus, (20, HEIGHT + 40))

        stam = wacky_font.render("Stamina: " + str(self.game.player.stamina), False, SUSFONT_COLOR)
        self.screen.blit(stam, (430, HEIGHT + 40))

        lvl = wacky_font.render("Level: " + str(self.game.map.current_level), False, SUSFONT_COLOR)
        self.screen.blit(lvl, (840, HEIGHT + 40))

        self.game.current_time = round(pg.time.get_ticks() / 1000)
        time = wacky_font.render(str(math.floor(self.game.current_time/60)) + ":" + str(self.game.current_time % 60), False, (0, 0, 0))
        self.screen.blit(time, (WIDTH - 175, 40))


###############################START MENU#################################

class MenuButton:
    def __init__(self, menu, pos, width, height, text, functionToCall, tag = None):
        self.menu = menu
        self.pos = pos; self.posx, self.posy = pos
        self.width = width
        self.height = height
        self.text = text
        self.functionToCall = functionToCall
        self.surf = pg.Surface((self.width, self.height))

        self.button_txt = self.menu.font.render(self.text, False, 'black')

        self.current_color = (200, 200, 200)

        self.mouse_over = False

        self.hidden = False

        self.lock_color_change = False

        self.tag = tag

        self.draw_button()

    def draw_button(self):
        self.surf.fill('skyblue')
        pg.draw.rect(self.surf, self.current_color, (0, 0, self.width, self.height), border_radius=5)
        self.surf.blit(self.button_txt, (self.width//2 - self.button_txt.get_width()//2, self.height//2 - self.button_txt.get_height()//2))

    def change_bright(self, mouseOver): #true/false changes brightness
        if self.lock_color_change:
            return

        if mouseOver:
            self.mouse_over = True
            self.current_color = (255, 255, 255)
        else:
            self.mouse_over = False
            self.current_color = (200, 200, 200)    
        
        self.draw_button()

    def update(self):
        if (self.posx <= self.menu.mouseX <= self.posx + self.width) and (self.posy <= self.menu.mouseY <= self.posy + self.height):
            self.change_bright(True)
        else:
            self.change_bright(False)

    def mouseClick(self):
        if self.mouse_over and not self.hidden:
            self.functionToCall()

    def draw(self):
        if not self.hidden:
            self.menu.screen.blit(self.surf, self.pos)

    def changeHidden(self, hidden):
        self.hidden = hidden
        self.change_bright(False)

class StartMenu:
    def __init__(self):
        self.mainscreen = pg.display.set_mode(ACTUALRES, pg.FULLSCREEN)
        self.screen = pg.Surface((WIDTH, HEIGHT + SHEIGHT)) # not a swear word, stands for s height
        self.screen.fill('skyblue')
        self.in_menu = True
        self.font = pg.font.Font(None, 65)
        self.mouseX, self.mouseY = pg.mouse.get_pos()
        self.buttons = []
        self.inCredits = False
        self.inOptions = False
        self.credits = pg.image.load('resources/sprites/credits.png')
        self.wacky_font = pg.font.Font('resources/textutil/wackyfont.ttf', 225)

    def update(self):
        self.mouseX, self.mouseY = pg.mouse.get_pos()
        self.mouseX *= RatioWidth
        self.mouseY *= RatioHeight * 1.22

    def get_button(self, buttonFunc):
        for but in self.buttons:
            if but.functionToCall == buttonFunc:
                return but

    def run(self):
        self.drawtitle()
        self.buttons.append(MenuButton(self, (HALF_WIDTH - 75, 300), 150, 75, "Play", self.play_button))
        self.buttons.append(MenuButton(self, (HALF_WIDTH - 100, 400), 200, 75, "Credits", self.credits_button))
        self.buttons.append(MenuButton(self, (HALF_WIDTH - 95, 500), 190, 75, "Options", self.options_button))
        self.buttons.append(MenuButton(self, (HALF_WIDTH - 75, 600), 150, 75, "Exit", self.exit_button))
        self.buttons.append(MenuButton(self, (1300, 75), 50, 50, "X", self.X_credits_button))
        self.buttons.append(MenuButton(self, (1300, 75), 50, 50, "X", self.X_options_button))
        self.buttons.append(MenuButton(self, (HALF_WIDTH - 200, 300), 400, 75, "Mouse Turning", self.mouse_turning, tag="options"))
        self.buttons.append(MenuButton(self, (HALF_WIDTH - 200, 400), 400, 75, "Key Turning", self.key_turning, tag="options"))

        self.get_button(self.X_credits_button).changeHidden(True)
        self.get_button(self.X_options_button).changeHidden(True)

        [but.changeHidden(True) for but in self.buttons if but.tag == "options"]

        while self.in_menu:
            if self.inCredits:
                self.update()
                self.screen.blit(self.credits, (HALF_WIDTH - self.credits.get_width()//2, HALF_HEIGHT - self.credits.get_height()//2))
                self.get_button(self.X_credits_button).update(); self.get_button(self.X_credits_button).draw()
    
                self.click_checks()

                transcreen = pg.transform.scale(self.screen, ACTUALRES)
                self.mainscreen.blit(transcreen, (0, 0))

                pg.display.flip()
                continue

            elif self.inOptions:
                self.update()

                self.get_button(self.X_options_button).update(); self.get_button(self.X_options_button).draw()
                [but.update() for but in self.buttons if but.tag == "options"]
                [but.draw() for but in self.buttons if but.tag == "options"]

                self.click_checks()

                transcreen = pg.transform.scale(self.screen, ACTUALRES)
                self.mainscreen.blit(transcreen, (0, 0))

                pg.display.flip()
                continue

            self.update()
            [but.update() for but in self.buttons]
            [but.draw() for but in self.buttons]
            self.click_checks()

            transcreen = pg.transform.scale(self.screen, ACTUALRES)
            self.mainscreen.blit(transcreen, (0, 0))

            pg.display.flip()
            
    def mouse_turning(self):
        global MouseRotation_Setting
        MouseRotation_Setting = True
        recalibrate_sensitivity(True)

    def key_turning(self):
        global MouseRotation_Setting
        MouseRotation_Setting = False
        recalibrate_sensitivity(False)
  
    def click_checks(self):
        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
                [but.mouseClick() for but in self.buttons]

    def exit_button(self):
        pg.quit()
        sys.exit()

    def play_button(self):
        self.in_menu = False
        
    def options_button(self):
        self.screen.fill('skyblue')

        self.inOptions = True
        [but.changeHidden(True) for but in self.buttons]
        [but.changeHidden(False) for but in self.buttons if but.tag == "options" and not but.functionToCall == self.X_credits_button]

        self.get_button(self.X_options_button).changeHidden(False)

        [but.update() for but in self.buttons]
        [but.draw() for but in self.buttons]

        pg.display.flip()

    def credits_button(self):
        self.screen.fill('skyblue')

        self.inCredits = True
        [but.changeHidden(True) for but in self.buttons]

        self.get_button(self.X_credits_button).changeHidden(False)

        [but.update() for but in self.buttons]
        [but.draw() for but in self.buttons]

        pg.display.flip()

    def X_options_button(self):
        self.screen.fill('skyblue')

        self.inOptions = False
        [but.changeHidden(False) for but in self.buttons if but.functionToCall != self.X_credits_button]
        [but.changeHidden(True) for but in self.buttons if but.tag == "options"]

        self.get_button(self.X_options_button).changeHidden(True)

        [but.update() for but in self.buttons]
        [but.draw() for but in self.buttons]

        pg.display.flip()

    def X_credits_button(self):
        self.screen.fill('skyblue')

        self.inCredits = False
        [but.changeHidden(False) for but in self.buttons if not but.functionToCall == self.X_options_button and not but.tag == "options"]
        self.get_button(self.X_credits_button).changeHidden(True)

        [but.update() for but in self.buttons]
        [but.draw() for but in self.buttons]

        pg.display.flip()
        
    def drawtitle(self):
        appliedTxt = self.wacky_font.render("Infiltrator", False, 'black')

        x, y = 360, 60

        self.screen.blit(appliedTxt, (x,y))


###########################LEVEL SELECTOR###############################

class levelselector:
    def __init__(self):
        self.font = pg.font.Font(None, 65)
        self.mainscreen = pg.display.set_mode(ACTUALRES, pg.FULLSCREEN)
        self.screen = pg.Surface((WIDTH, HEIGHT + SHEIGHT)) # not a swear word, stands for s height
        self.screen.fill('skyblue')
        self.wacky_font = pg.font.Font('resources/textutil/wackyfont.ttf', 150)
        self.chooselevel = True
        self.mouseX, self.mouseY = pg.mouse.get_pos()
        self.buttons = []
        self.buttons.append(MenuButton(self, (HALF_WIDTH - 600, 350), 300, 75, "Building 1", self.play_button))
        
    def update(self):
        self.mouseX, self.mouseY = pg.mouse.get_pos()
        self.mouseX *= RatioWidth
        self.mouseY *= RatioHeight * 1.22
        
    def drawtitle(self):
        text = self.wacky_font.render("Building Selector", False, 'black')

        x, y = 375, 60

        self.screen.blit(text, (x,y))

    def play_button(self):
        self.chooselevel = False

    def run(self):
        self.screen.fill('skyblue')
        self.drawtitle()
        
        while self.chooselevel:
            self.update()
            [but.update() for but in self.buttons]
            [but.draw() for but in self.buttons]
            self.click_checks()

            transcreen = pg.transform.scale(self.screen, ACTUALRES)
            self.mainscreen.blit(transcreen, (0, 0))

            pg.display.flip()
            
    def click_checks(self):
        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
                [but.mouseClick() for but in self.buttons]
            
        

###GAME CODE###


#game class, the most important in the script, all function stem from this class, controls everything, basically god
class Game:
    #def vars, init func
    def __init__(self):
        self.mainscreen = pg.display.set_mode(ACTUALRES, pg.FULLSCREEN) #not a swear work, it is screen height
        self.screen = pg.Surface((WIDTH, HEIGHT + SHEIGHT))
        self.clock = pg.time.Clock()
        self.delta_time = 1
        self.current_time = 0
        self.high_score = 0

        self.mouseShowing = False
        if MouseRotation_Setting:
            self.setMouseVisibility(False)

        #event for animation i think
        self.global_trigger = False
        self.global_event = pg.USEREVENT + 0

        #event for adding chars to the textbox
        self.next_char_trigger = False
        self.next_char_event = pg.USEREVENT + 1

        self.check_touching_trigger = False
        self.check_touching_event = pg.USEREVENT + 2

        #event for turning portal
        self.portal_event = pg.USEREVENT + 2

        pg.time.set_timer(self.global_event, 40)
        pg.time.set_timer(self.check_touching_event, TOUCH_CHECK_TIME)
        pg.time.set_timer(self.next_char_event, 10)
        pg.time.set_timer(self.portal_event, 200)
        #dictionary of key isPressed?
        self.keys = {
            pg.K_w: False,
            pg.K_s: False,
            pg.K_a: False,
            pg.K_d: False,
            pg.K_LEFT: False,
            pg.K_RIGHT: False,
            pg.K_LSHIFT: False
        }
        self.new_game()

    def setMouseVisibility(self, bool): self.mouseShowing = bool; pg.mouse.set_visible(bool)

    def win_game(self):
        self.object_renderer.show_win_screen()

        font = self.display_menu.wacky_font

        self.high_score = round(self.current_time * (1 + self.player.stealth/10) - (self.inventory_system.meme_number() * 100))

        hs = font.render("Score: " + str(self.high_score), False, (0, 0, 0))
        self.screen.blit(hs, (HALF_WIDTH - hs.get_width()//2, HALF_HEIGHT - hs.get_height()//2))

        #self.sound_player.stop_sound("theme"); self.sound_player.load_sound("winning", 'resources/sound/win.wav'); self.sound_player.play_sound("winning", volume=0.4, loop=False)
        
        pg.transform.scale(self.screen, ACTUALRES, self.mainscreen)

        pg.display.flip()

        pg.time.wait(7500)

        pg.quit()
        sys.exit()

    def lose_game(self):
        self.object_renderer.game_over()

        pg.transform.scale(self.screen, ACTUALRES, self.mainscreen)

        pg.display.flip()

        pg.time.wait(7500)

        pg.quit()
        sys.exit()

    #creates instances of all neccesary classes and starts of the game
    def new_game(self):
        self.current_time = 0
        self.sound_player = SoundPlayer(); self.sound_player.play_sound("theme", volume=0.2, loop=True)
        self.map = Map(self)
        self.pathfinding = PathFinding(self)
        self.player = Player(self)
        self.inventory_system = InventorySystem(self)
        self.object_renderer = ObjectRenderer(self)
        self.raycasting = RayCasting(self)
        self.object_handler = ObjectHandler(self)
        self.sound = Sound(self)
        self.statbar = StatBar(self)
        self.text_box = TextBox(self, 200, HALF_HEIGHT + HALF_HEIGHT // 2, HALF_WIDTH + HALF_WIDTH // 2, HALF_HEIGHT // 2)
        self.display_menu = DisplayMenu(self)
        self.pawn_shop = PawnShopMenu(self)

    #updates everything that needs updating
    def update(self):
        self.player.update()
        self.raycasting.update()
        self.object_handler.update()
        self.text_box.update()
        self.display_menu.update()
        
        #self.animated_sprite.update()
        pg.display.flip()
        self.delta_time = self.clock.tick(FPS)

        pg.display.set_caption(f'Infiltrator - {self.clock.get_fps() :.1f}')

        #pg.display.set_icon(pg.image.load('resources/sprites/logo.png'))


    #draws stuff
    def draw(self):
        self.object_renderer.draw()
        self.statbar.draw()
        self.display_menu.draw()

        self.text_box.draw()
        self.object_renderer.draw_npc_talker()

        self.pawn_shop.draw()

        #minimap thingy
        #self.map.draw()
        #self.player.draw()

        pg.transform.scale(self.screen, ACTUALRES, self.mainscreen)

    #checks pygame events for key pressed and quits
    def check_events(self):
        self.global_trigger = False
        self.check_touching_trigger = False
        self.next_char_trigger = False
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            #an event that is triggered every... i think 40 ms...
            if event.type == self.global_event:
                self.global_trigger = True

            elif event.type == self.check_touching_event:
                self.check_touching_trigger = True

            elif event.type == self.next_char_event:
                self.next_char_trigger = True
                self.object_renderer.popup_update()

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_F4 or event.key == pg.K_BACKSLASH:
                    pg.quit()
                    sys.exit()
                else:
                    self.keys[event.key] = True
                self.text_box.event_call(event)
                self.display_menu.event_call(event)
                [passive.event_call(event) for passive in self.object_handler.passive_list]
            if event.type == pg.KEYUP:
                self.keys[event.key] = False

            if event.type == pg.MOUSEBUTTONDOWN:
                self.pawn_shop.check_slot_click()

    #main run loop
    def run(self):
        while 1:
            self.check_events()
            self.update()
            self.draw()

#starts the game
if __name__ == '__main__':
    pg.init()

    start_menu = StartMenu()
    start_menu.run()
    
    #levelselector = levelselector()
    #levelselector.run()
    
    game = Game()
    game.run()