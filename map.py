import pygame
import os
import json
import living
from functions import draw_text

class Map(pygame.sprite.Sprite):
    def __init__(self, wallGroup, enemyGroup, teleporters, chests, name="starter_room", to_tp = -1):
        pygame.sprite.Sprite.__init__(self)
        
        wallGroup.empty()
        enemyGroup.empty()
        teleporters.empty()
        chests.empty()
        
        self.name = name
        DATA = {}
        with open("map_data\\{0}.json".format(name), "r") as DATA:
            DATA = json.load(DATA)
            self.DATA = DATA
        self.width = DATA["width"]*20
        self.height = DATA["height"]*20
        self.image = pygame.Surface([self.width, self.height])
        self.default_image = pygame.image.load("image\\Map images\\{0}.png".format(name))
        self.MC_pos = [x*20 for x in DATA["living"]["MC"]["pos"]]
        for count in range(len(DATA["blocks"]["wall"]["X"])):
            wallGroup.add(Wall([DATA["blocks"]["wall"]["X"][count], DATA["blocks"]["wall"]["Y"][count], 20, 20]))
        for count in range(len(DATA["living"]["enemy1"]["X"])):
            enemyGroup.add(living.Enemy1(self, 100, count))
        for count in range(len(DATA["blocks"]["teleporter"]["each"])):
            data = DATA["blocks"]["teleporter"]["each"][count]
            teleporter = Teleporter(data["to_room"], data["ID"], data["to_ID"], [data["X"]*20, data["Y"]*20])
            teleporters.add(teleporter)
            if teleporter.ID == to_tp:
                self.MC_pos = [teleporter.x+10, teleporter.y+10]
        for count in range(len(DATA["blocks"]["chest"]["each"])):
            data = DATA["blocks"]["chest"]["each"][count]
            chests.add(Chest([data["X"], data["Y"]], data["items"]))

class Wall(pygame.sprite.Sprite):
    
    def __init__(self, pos, range = 0):
        pygame.sprite.Sprite.__init__(self)
        self.pos = [pos[0], pos[1]]
        self.x, self.y, self.width, self.height = pos[0]*20, pos[1]*20, pos[2], pos[3]
        self.right, self.bottom = self.x + self.width, self.y + self.height
        self.center = [self.x + self.width / 2, self.y + self.height / 2]
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(pygame.Color(255, 255, 255))
        self.rect = self.image.get_rect(topleft=[self.x, self.y])

    def moveSelf(self, x, y):
        self.x += x
        self.y += y
        self.right, self.bottom = self.x + self.width, self.y + self.height
        # self.center[0] += x
        self.center[1] += y
        self.rect = self.rect.move(x, y)
        return


class Chest(pygame.sprite.Sprite):

    def __init__(self, pos, items):
        pygame.sprite.Sprite.__init__(self)


        self.closedImage = pygame.image.load("image\\chest_1.png")
        self.openedImage = pygame.image.load("image\\chest_2.png")

        self.x, self.y = pos[0]*20, pos[1]*20

        self.image = self.closedImage.copy()

        self.items = items

        self.opened = False
        self.rect = self.image.get_rect(topleft=[self.x, self.y])
    
    def update(self, MC):
        if self.opened:
            return
        if self.rect.colliderect(MC.rect):
            self.opened = True
            self.image = self.openedImage.copy()
            if "heal" in self.items:
                MC.food += 1
            if "key1" in self.items:
                MC.key_1 = 1
            if "key2" in self.items:
                MC.key_2 = 1


class Item(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.x = 1050
        self.y = 600
        
        self.food_img = pygame.image.load("image\\food.png")
        
        self.key_1_img = pygame.image.load("image\\key-1.png")
        self.key_1_img.set_colorkey(pygame.Color(255, 255, 255))
        
        self.key_2_img = pygame.image.load("image\\key-2.png")
        self.key_2_img.set_colorkey(pygame.Color(255, 255, 255))
        
        self.bg = pygame.Color(0, 0, 0)
        self.textcolor = pygame.Color(128, 128, 128)
        
        self.image = pygame.Surface([225, 45])

    def drawSelf(self, screen, MC):
        self.image.fill(self.bg)
        self.image.set_colorkey(pygame.Color(0, 0, 0))
        self.image.blit(self.key_1_img, [0, 0])
        self.image.blit(self.key_2_img, [60, 0])
        self.image.blit(self.food_img, [120, 13])
        draw_text(self.image, str(MC.key_1), 50, 30, 13, self.textcolor)
        draw_text(self.image, str(MC.key_2), 50, 90, 13, self.textcolor)
        draw_text(self.image, str(MC.food), 50, 160, 13, self.textcolor)
        screen.blit(self.image, [self.x, self.y])


class Teleporter(pygame.sprite.Sprite):
    def __init__(self, to_room, ID, to_ID, pos):
        pygame.sprite.Sprite.__init__(self)

        self.to_room = to_room
        self.ID = ID
        self.to_ID = to_ID
        
        self.x = pos[0]
        self.y = pos[1]
        self.rect = pygame.Rect(pos, [80, 120])
    
    def check(self, MC, mapName):
        print(self.to_room, MC.key_1, MC.key_2)
        if self.to_room == "bossroom" and not MC.key_2:
            return None
        if self.to_room == "basement" and not MC.key_1:
            return None
        if self.rect.colliderect(MC.rect):
            return self.to_room, self.to_ID
    

class NPC(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface([80, 100])
        self.x = 4600
        self.y = 80
        self.image.fill(pygame.Color(128, 64, 0))
        
        eye = pygame.Rect(10, 20, 10, 15)
        pygame.draw.rect(self.image, pygame.Color(225, 225, 225), eye)
        
        blood = pygame.Rect(0, 50, 80, 50)
        pygame.draw.rect(self.image, pygame.Color(225, 0, 0), blood)
        
        self.rect = pygame.Rect(4600, 80, 80, 100)





