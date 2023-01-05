import pygame
import json
from os import listdir, remove
from os.path import isfile, join, dirname
from operator import itemgetter
from sort import sorting, getFile, getData

pygame.init()

resolution = [1280, 720]
screen = pygame.display.set_mode(resolution, pygame.FULLSCREEN)

fileType = "json"
WHITE = pygame.Color(255, 255, 255)
BLACK = pygame.Color(0, 0, 0)
GREY = pygame.Color(128, 128, 128)
BLUEGREY = pygame.Color(90, 110, 120)
GREENGREY = pygame.Color(185, 200, 170)
FONT  = pygame.font.SysFont("arial", 32)

blockImage = { \
    "wall": pygame.image.load("..\\image\\wall.png"), \
    "teleporter": pygame.image.load("..\\image\\teleporter.png"), \
    "chest": pygame.image.load("..\\image\\chest_1.png"), \
    "MC": pygame.Surface([60, 100]), \
    "enemy1": pygame.Surface([60, 100]), \
    "enemy2": pygame.Surface([60, 100]), \
    "enemyPath": pygame.Surface([20, 20])\
}
blockImage["MC"].fill(pygame.Color(0, 255, 0))
blockImage["enemy1"].fill(pygame.Color(200, 50, 0))
blockImage["enemy2"].fill(pygame.Color(200, 0, 50))
blockImage["enemyPath"].fill(pygame.Color(255, 0, 0))

blockSize = 20
gridGap = 2

def main():
    global fileType
    
    frame = pygame.time.Clock()
    
    screen.fill(BLUEGREY)
    
    scrolly = 0
    moveMap = False
    mousePos = []
    mouseMove = []
    running = 1
    holdingESC = False
    maps = MapSelector(getFile(fileType))
    mapData = None
    
    while running:
        screen.fill(BLUEGREY)
        
        keyPressed = pygame.key.get_pressed()
        if keyPressed[pygame.K_ESCAPE] and not holdingESC:
            running -= 1
            holdingESC = True
            if running == 1:
                maps.active = True
                mapData = mapData.save_all(True)
        elif not keyPressed[pygame.K_ESCAPE] and holdingESC:
            holdingESC = False
        
        mouseMove = pygame.mouse.get_rel()
        mousePos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if mapData and event.type == pygame.KEYDOWN:
                print("k d")
                keyPressed = pygame.key.get_pressed()
                if keyPressed[pygame.K_1]:
                    blockButtons = mapData.buttons
                    for each in blockButtons:
                        each.activate()
                    m_pos = [1201, 81 + 0*195]
                    for each in mapData.modeButton:
                        each.doBlink(m_pos)
                    mapData.changeMode(m_pos, screen)
                elif keyPressed[pygame.K_2]:
                    blockButtons = mapData.buttons
                    for each in blockButtons:
                        each.activate()
                    m_pos = [1201, 81 + 1*195]
                    for each in mapData.modeButton:
                        each.doBlink(m_pos)
                    mapData.changeMode(m_pos, screen)
                elif keyPressed[pygame.K_3]:
                    blockButtons = mapData.buttons
                    for each in blockButtons:
                        each.activate()
                    m_pos = [1201, 81 + 2*195]
                    for each in mapData.modeButton:
                        each.doBlink(m_pos)
                    mapData.changeMode(m_pos, screen)
            if event.type == pygame.MOUSEWHEEL:
                scrolly += event.y * 15
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if maps.active:
                        for each in maps.mapButtons:
                            if each.blinking:
                                maps.reset()
                                running += 1
                                screen.fill(GREENGREY)
                                loadingText = pygame.font.Font(None, 200).render("Loading...", True, WHITE)
                                screen.blit(loadingText, [290, 280])
                                pygame.display.flip()
                                mapData = MapData(each.name+".json", screen)
                                continue
                    if mapData and not mapData.grid.blinking:
                            blockButtons = mapData.buttons
                            for each in blockButtons:
                                each.activate()
                            mapData.changeMode(mousePos, screen)
        
        if running == 1:
            scrolly = int(scrolly *6/7)
            maps.update(scrolly)
            screen.blit(maps.image, [maps.x, maps.y])
        elif running == 2:
            mapGrid = mapData.grid
            blockButtons = mapData.buttons
            modeButtons = mapData.modeButton
            
            mouseButton = pygame.mouse.get_pressed()
            
            if mapGrid.blinking:
                if moveMap:
                    mapGrid.move(mouseMove)
                moveMap = mouseButton[1]
                if mouseButton[0]:
                    gridPos = [mousePos[0]-mapGrid.x-mapGrid.mapx, mousePos[1]-mapGrid.y-mapGrid.mapy]
                    if gridPos[0] not in [0,1] and gridPos[1] not in [0,1]:
                        gridPos = [int(gridPos[0]/22), int(gridPos[1]/22)]
                        for each in blockButtons:
                            if each.active:
                                size = [1, 1]
                                if mapGrid.type != "enemyPath":
                                    size = mapData.data[mapGrid.type][each.name]["size"]
                                mapGrid.deleteElement(mousePos)
                                block = mapGrid.addBlock(each.name, gridPos, mapGrid.type, size)
                                for count, each in enumerate(mapGrid.blocks[:len(mapGrid.blocks)-1]):
                                    if each.rect.colliderect(block.rect):
                                        print("deleted", mapGrid.deleteElement([each.screenx+mapGrid.mapx+1, each.screeny+mapGrid.mapy+1]), "due to collision")
                                        block.drawSelf(mapGrid.mapImage)
                                        mapGrid.image.blit(mapGrid.mapImage, [mapGrid.mapx, mapGrid.mapy])
                                        frame.tick(30)
                if mouseButton[2]:
                    mapGrid.deleteElement(mousePos)
            
            mapData.update(mousePos, screen)
            screen.blit(mapGrid.image, [mapGrid.x, mapGrid.y])
            for each in blockButtons:
                screen.blit(each.image, [each.x, each.y])
            for each in modeButtons:
                screen.blit(each.image, [each.x, each.y])
    
        frame.tick(30)
        pygame.display.flip()
    
    pygame.quit()

# running = 1

class MapSelector: # Drawn on screen
    def __init__(self, maps):
        self.active = True
        self.x = 140
        self.y = 0
        self.height = len(maps)*100
        self.mapButtons = []
        self.image = pygame.Surface([1000, self.height])
        self.image.fill(GREY)
        for count, each in enumerate(maps):
            self.mapButtons.append(MapButton(each, count))
            each = self.mapButtons[count]
            self.image.blit(each.image, [each.x, each.y])
    
    def update(self, y):
        prevy = self.y
        self.y += y
        if self.y > 620:
            self.y = 620
        elif self.y < 100 - self.height:
            self.y = 100 - self.height
        movey = self.y - prevy
        for each in self.mapButtons:
            each.rect = each.rect.move(0, movey)
            each.doBlink(pygame.mouse.get_pos())
            self.image.blit(each.image, [each.x, each.y])
        return
    
    def reset(self):
        self.active = False
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        return
    
class MapButton: # Drawn on MapSelector
    def __init__(self, name, index):
        self.x = 5
        self.y = index * 100 + 5
        self.index = index
        self.rect = pygame.Rect(self.x+140, self.y+0, 990, 90)
        self.blinking = False
        self.name = name
        self.buttonRect = pygame.Rect(0, 0, 989, 89)
        self.textB = FONT.render(name.split(".")[0].upper(), True, BLACK)
        # self.textW = FONT.render(name.split(".")[0].upper(), True, GREENGREY)
        self.textWidth = self.textB.get_width()
        
        self.image = pygame.Surface([990, 90])
        self.image.fill(GREENGREY)
        pygame.draw.rect(self.image, BLACK, self.buttonRect, 2)
        self.image.blit(self.textB, [int((1000-self.textWidth)/2), 26])
    
    def doBlink(self, pos):
        if not self.blinking and self.rect.collidepoint(pos):
            self.image.fill(WHITE)
            pygame.draw.rect(self.image, GREENGREY, self.buttonRect, 2)
            self.image.blit(self.textB, [int((1000-self.textWidth)/2), 26])
            self.blinking = True
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            return
        if self.blinking and not self.rect.collidepoint(pos):
            self.image.fill(GREENGREY)
            pygame.draw.rect(self.image, BLACK, self.buttonRect, 2)
            self.image.blit(self.textB, [int((1000-self.textWidth)/2), 26])
            self.blinking = False
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            return

#running = 2

class MapData: # Not visible
    def __init__(self, name, screen, type="blocks"):
        self.name = name
        self.data = getData(name)
        self.type = type
        self.gridPos = [450, 80]
        self.grid = MapGrid(self.data, self.gridPos, type)
        self.buttons = []
        self.modeButton = []
        for count, each in enumerate(self.data[type]):
            self.buttons.append(BlockButton(count, each))
        for count in range(3):
            self.modeButton.append(ModeButton(count, screen))
    
    def rebuild(self, screen, type):
        self.save_all(False)
        self.type = type
        self.grid = MapGrid(self.data, self.gridPos, type, [self.grid.mapx, self.grid.mapy])
        self.buttons = []
        if type == "enemyPath":
            self.buttons.append(BlockButton(0, type))
            return self
        for count, each in enumerate(self.data[type]):
            self.buttons.append(BlockButton(count, each))
    
    def update(self, pos, screen):
        self.grid.doBlink(pos)
        for each in self.buttons:
            each.doBlink(pos)
        for each in self.modeButton:
            each.doBlink(pos)
            if each.active:
                screen.blit(each.textFont.render("Editing {0}".format(each.name), True, BLACK), [450, 650])
    
    def changeMode(self, pos, screen):
        for each in self.modeButton:
            if each.blinking:
                for button in self.modeButton:
                    button.disable()
                each.activate()
                self.rebuild(screen, each.name)
    
    def save_all(self, saveFile_b):
        type = self.type
        data = self.data[type]
        if type == "blocks": # DATALOADER
            for each in data: # reset data
                if each in ["wall"]:
                    data[each]["X"], data[each]["Y"] = [[], []]
                else:
                    data[each]["each"] = []
            for each in self.grid.blocks:
                x, y = each.pos
                name = each.name
                if name in ["wall"]:
                    data[name]["X"].append(x)
                    data[name]["Y"].append(y)
                elif name == "chest":
                    data[name]["each"].append({"X":each.pos[0], "Y":each.pos[1], "items":"heal"})
                else:
                    data[name]["each"].append({"X":each.pos[0], "Y":each.pos[1], "to_room":"", "to_ID": None, "ID": None})
        if type == "living":
            for each in data:
                if each != "MC":
                    data[each]["X"], data[each]["Y"] = [], []
            for each in self.grid.blocks:
                x, y = each.pos
                name = each.name
                if name == "MC":
                    data[name]["pos"] = [x, y]
                else:
                    data[name]["X"].append(x)
                    data[name]["Y"].append(y)
        if type == "enemyPath":
            data["X"], data["Y"] = [], []
            for each in self.grid.blocks:
                x, y = each.pos
                data["X"].append(x)
                data["Y"].append(y)
        self.data[type].update(data)
        # self.data = sorting(self.data)
        if saveFile_b:
            with open(self.name, "w") as file:
                json.dump(self.data, file)
            self.draw_map(True)
        return
    
    def draw_map(self, saveFile_b):
        mapImage = pygame.Surface([self.data["width"]*20, self.data["height"]*20])
        mapImage.fill(pygame.Color(0, 0, 0))
        for name in self.data:
            if name in ["width", "height"]:
                continue
            data = self.data[name]
            for name in data:
                each = data[name]
                if name == "wall":
                    for count in range(len(each["X"])):
                        mapImage.blit(blockImage["wall"], [each["X"][count]*20, each["Y"][count]*20])
                elif name in ["teleporter"]:
                    for count in range(len(each["each"])):
                        n = each["each"][count]
                        mapImage.blit(blockImage[name], [n["X"]*20, n["Y"]*20])
        
        if saveFile_b:
            pygame.image.save(mapImage, "..\\image\\Map images\\{0}.png".format(self.name.split(".")[0]))
        return mapImage

class MapGrid: # Drawn on screen
    def __init__(self, mapData, pos, type="blocks", mappos=[0, 0]):
        self.x, self.y = pos[0], pos[1]
        self.mapx, self.mapy = mappos
        self.type = type
        self.blockWidth, self.blockHeight = mapData["width"], mapData["height"]
        self.width, self.height = self.blockWidth*22+2, self.blockHeight*22+2
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.blinking = False
        
        self.imageSize = [ \
            720 if 720 < self.width else self.width,  \
            560 if 560 < self.height else self.height \
            ]
        self.image = pygame.Surface(self.imageSize)
        self.rect = self.image.get_rect(topleft = [self.x, self.y])
        self.mapImage = pygame.Surface([self.width, self.height])
        self.blocks = []
        self.draw_grid([0, 0], [self.blockWidth, self.blockHeight])
        for blockName in mapData[type]:
            blockData = mapData[type][blockName]
            if blockName in ["chest", "teleporter"]:
                for each in blockData["each"]:
                    self.addBlock(blockName, [each["X"], each["Y"]], type, blockData["size"])
            elif blockName == "MC":
                self.addBlock("MC", blockData["pos"], type, blockData["size"])
            elif blockName in ["enemy1", "enemy2"]:
                for count in range(len(blockData["X"])):
                    self.addBlock(blockName, [blockData["X"][count], blockData["Y"][count]], type, blockData["size"])
            elif blockName == "X" and type == "enemyPath":
                for count in range(len(blockData)):
                    self.addBlock("enemyPath", [mapData[type]["X"][count], mapData[type]["Y"][count]], "enemyPath", [1, 1])
                break
            else:
                for count in range(len(blockData["X"])):
                    pos = [blockData["X"][count], blockData["Y"][count]]
                    self.blocks.append(MapBlock(blockName, pos, [self.x, self.y], type, blockData["size"]))
                    currentBlock = self.blocks[count]
                    currentBlock.drawSelf(self.mapImage)
        self.image.blit(self.mapImage, [self.mapx, self.mapy])
    
    def addBlock(self, name, pos, type, size):
        if name == "MC":
            for each in self.blocks:
                if each.name == "MC":
                    temppos = self.deleteElement([each.screenx+self.mapx+1, each.screeny+self.mapy+1])[1]
                    self.draw_grid(pos, [3, 5])
        index = len(self.blocks)
        self.blocks.append(MapBlock(name, pos, [self.x, self.y], type, size))
        block = self.blocks[index]
        block.drawSelf(self.mapImage)
        self.image.blit(self.mapImage, [self.mapx, self.mapy])
        return block
    
    def doBlink(self, pos):
        if not self.blinking and self.rect.collidepoint(pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
            self.blinking = True
            return
        if self.blinking and not self.rect.collidepoint(pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            self.blinking = False
            return
    
    def move(self, move):
        self.mapx += move[0]
        self.mapy += move[1]
        if self.mapy + self.height < self.imageSize[1]:
            self.mapy = self.imageSize[1] - self.height
        if self.mapy > 0:
            self.mapy = 0
        if self.mapx + self.width < self.imageSize[0]:
            self.mapx = self.imageSize[0] - self.width
        if self.mapx > 0:
            self.mapx = 0
        self.image.fill(BLACK)
        self.image.blit(self.mapImage, [self.mapx, self.mapy])
        return
    
    def draw_grid(self, pos, size):
        x = pos[0]*22
        y = pos[1]*22
        width = size[0]*22+2
        height = size[1]*22+2
        pygame.draw.rect(self.mapImage, BLACK, pygame.Rect(x, y, width, height))
        for tempx in range(size[0]):
            for tempy in range(size[1]):
                tempRect = pygame.Rect(x+tempx*22+2, y+tempy*22+2, 20, 20)
                pygame.draw.rect(self.mapImage, WHITE, tempRect)

    def deleteElement(self, mousePos):
        x, y = mousePos
        for count, each in enumerate(self.blocks):
            if x >= each.screenx + self.mapx and x < each.screenRight + self.mapx and y >= each.screeny + self.mapy and y < each.screenBottom + self.mapy:
                block = self.blocks[count]
                name = block.name
                size = block.size.copy()
                pos = block.pos.copy()
                self.draw_grid(pos, size)
                self.blocks.pop(count)
                self.image.blit(self.mapImage, [self.mapx, self.mapy])
                return name, pos, size

class MapBlock: #Drawn on grid
    def __init__(self, name, pos, gridPos, type, size=[1, 1]):
        self.x = pos[0]*22+(size[0]-1)+2
        self.y = pos[1]*22+(size[1]-1)+2 # *20?
        self.right = self.x + size[0]*20
        self.bottom = self.y + size[1]*20
        self.screenx = self.x + gridPos[0]
        self.screeny = self.y + gridPos[1]
        self.screenRight = self.right + gridPos[0]
        self.screenBottom = self.bottom + gridPos[1]
        self.pos = pos
        self.size = size
        self.name = name
        self.type = type
        self.image = blockImage[name]
        self.rect = pygame.Rect(self.x-size[0]+1, self.y-size[1]+1, size[0]*22-2, size[1]*22-2)
    
    def drawSelf(self, mapImage):
        mapImage.blit(self.image, [self.x, self.y])
        return

class BlockButton: # Drawn on screen
    def __init__(self, index, block):
        default_pos = [80, 80]
        self.x = default_pos[0]
        self.y = default_pos[1] + index * 110
        self.width = 300
        self.height = 90
        self.name = block
        self.blinking = False
        self.active = False
        
        self.image = pygame.Surface([self.width, self.height])
        self.rect = pygame.Rect(self.x, self.y, self.width-1, self.height-1)
        self.innerRect = pygame.Rect(2, 2, self.width-4, self.height-4)
        self.textFont = pygame.font.Font(None, 50)
        self.textPos = (93, 29)
        
        self.image.fill(BLACK)
        pygame.draw.rect(self.image, GREENGREY, self.innerRect)
        self.image.blit(blockImage[self.name], [5, 5])
        self.image.blit(self.textFont.render(block, True, BLACK), self.textPos)
    
    def doBlink(self, pos):
        if not self.blinking and self.rect.collidepoint(pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            self.blinking = True
            return
        if self.blinking and not self.rect.collidepoint(pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            self.blinking = False
            return
        
    def activate(self):
        if self.blinking:
            self.image.fill(GREENGREY)
            pygame.draw.rect(self.image, WHITE, self.innerRect)
            self.image.blit(blockImage[self.name], [5, 5])
            self.image.blit(self.textFont.render(self.name, True, BLACK), self.textPos)
            self.active = True
            return True
        else:
            self.image.fill(BLACK)
            pygame.draw.rect(self.image, GREENGREY, self.innerRect)
            self.image.blit(blockImage[self.name], [5, 5])
            self.image.blit(self.textFont.render(self.name, True, BLACK), self.textPos)
            self.active = False
            return False

class ModeButton:
    def  __init__(self, index, screen): # index = 0~2
        self.active = False
        self.blinking = False
        if not index:
            self.name = "blocks"
            self.blinking = True
        elif index == 1:
            self.name = "living"
        else:
            self.name = "enemyPath"
        self.index = index
        self.x = 1200 
        self.y = 80 + index*195
        self.width, self.height = 50, 170
        self.textPos = [16, 67]
        self.image = pygame.Surface([self.width, self.height])
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.innerRect = pygame.Rect(2, 2, self.width-4, self.height-4)
        self.textFont = pygame.font.Font(None, 50)
    
    def doBlink(self, pos):
        if not self.blinking and self.rect.collidepoint(pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            self.blinking = True
            return
        if self.blinking and not self.rect.collidepoint(pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            self.blinking = False
            return
    
    def activate(self):
        if self.blinking:
            self.image.fill(GREENGREY)
            pygame.draw.rect(self.image, WHITE, self.innerRect)
            self.image.blit(self.textFont.render(str(self.index+1), True, BLACK), self.textPos)
            self.active = True
            self.blinking = False
            return True
        return False
    
    def disable(self):
        self.image.fill(BLACK)
        pygame.draw.rect(self.image, GREENGREY, self.innerRect)
        self.image.blit(self.textFont.render(str(self.index+1), True, BLACK), self.textPos)
        self.active = False
        return False

# end

if __name__ == "__main__":
    main()






while True:
    
    mouseMove = pygame.mouse.get_rel()
    mousePos = pygame.mouse.get_pos()
    
    if leftClick:
        for each in modeButtons:
            if each.collidepoint(mousePos):
                each.activate()
                mapData.changeMode(each.name)
                mapData.rebuild()
        for each in blockButtons:
            if each.collidepoint(mousePos):
                each.activate()
        if mapGrid.collidepoint(mousePos):
            for each in blockButtons:
                if each.active:
                    mapGrid.addBlock(each.name, mousePos)
                    break
    
    if rightClick:
        if mapGrid.collidepoint(mousePos):
            mapGrid.deleteElement(mousePos)
    
    if middleClick:
        mapGrid.move(mouseMove)
        
    
    frame.tick(30)
        















