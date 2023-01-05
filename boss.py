from numpy import e
import pygame
import map
import random

class Boss(pygame.sprite.Sprite):

    def __init__(self, mapD):
        pygame.sprite.Sprite.__init__(self)

        self.BossMove  = []
        for count in range(1, 15):
            self.BossMove.append(pygame.image.load("image\\boss\\boss walk\\boss walk{0}.png".format(str(count))))
        self.Bossattack = pygame.image.load("image\\boss\\boss attack\\boss attack1.png")
        self.Bossdash1 = pygame.image.load("image\\boss\\bossdash\\boss dash1.png")
        self.Bossdash2 = pygame.image.load("image\\boss\\bossdash\\boss dash2.png")
        self.Bossdash3 = pygame.image.load("image\\boss\\bossdash\\boss dash3.png")

        self.attackCooldown = 0
        self.skillCooldown = 0 # 0 = can attack
        self.jumpCooldown = 0
        self.faceDir = 0
        self.status = 1
        # Status: stunned = -1, died = 0, move = 1, attack = 2, dash = 3
        self.frame = 0
        self.tempframe = 0
        self.health = 500
        self.immunity = False
        self.onGround = False
        self.x, self.y = 0, 0
        self.width, self.height = 300, 200
        self.max_x = mapD.width - self.width
        self.max_y = mapD.height - self.height - 20
        self.right, self.bottom = self.x + self.width, self.y + self.height
        self.center = [self.x + self.width / 2, self.y + self.height / 2]
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.xSpeed, self.ySpeed = 0, 0
        
        
        self.attack = pygame.sprite.Group()
        self.attacked = pygame.sprite.Group()
    
    def dash(self):
        if self.skillCooldown:
            if self.tempframe < 30:
                if self.tempframe > 15:
                    self.xSpeed = (self.faceDir*2-1)*(30-self.tempframe)*2
                    self.image = self.Bossdash2.copy()
                else:
                    self.xSpeed = 0
                    self.image = self.Bossdash1.copy()
                return None
            else:
                self.status = 1
                return True
        self.status = 3
        self.tempframe = 0
        self.skillCooldown = 90
        return False
    
    def doattack(self):
        if self.attackCooldown:
            if self.tempframe < 30:
                if self.tempframe == 15:
                    self.attack.add(Attack(self))
                return None
            else:
                self.status = 1
                return True
        self.status = 2
        self.tempframe = 0
        self.attackCooldown = 90
        return False
    
    def processDamage(self, MC):
        mcattack = pygame.sprite.spritecollide(self, MC.attack, False)
        mcbullet = pygame.sprite.spritecollide(self, MC.attack2, False)
        #防止傷害重複
        if mcattack:
            wasAttacked = False
            for each in mcattack:
                if each not in self.attacked:
                    wasAttacked = True
                    self.attacked.add(each)
            if wasAttacked:
                self.health -= 20
                MC.ySpeed -= 2
                MC.onGround = False
                if MC.center[0]-self.center[0] > 0:
                    MC.xSpeed += 3
                    MC._fix_pos()
                else:
                    MC.xSpeed -= 3
                    MC._fix_pos()
        if mcbullet:
            wasAttacked = False
            for each in mcbullet:
                if each not in self.attacked:
                    wasAttacked = True
                    self.attacked.add(each)
            if wasAttacked:
                self.health -= 40
        return
    
    def processMove(self, MC):
        #走向主角
        if self.frame % 30 == 0:
            dir = random.randint(-2, 10)
            if dir > 0:
                dir = 1
            elif not dir:
                dir = 0
            else:
                dir = -1
            if MC.center[0] < self.x:
                self.xSpeed = -5*dir
                self.faceDir = 0
            elif MC.center[0] > self.right:
                self.xSpeed = 5*dir
                self.faceDir = 1
            else:
                self.xSpeed = 0

        #跳躍
        #if self.y == self.max_y:
        if (self.center[1] - MC.center[1] > 80 or not random.randint(0, 89)) and not self.jumpCooldown:
            self.ySpeed -= 44
            self.jumpCooldown = 25
            self.onGround = False
        
        if random.randint(0, 10) * self.tempframe > 1000:
            self.status = (random.randint(0, 3) > 0) +2
    
    def update(self, MC, wallGroup):
        self.frame += 1
        self.tempframe += 1
        self.processDamage(MC)
        #移動
        self.x += self.xSpeed
        self.y += self.ySpeed
        self.fix_pos("xy")
        
        if self.status == -1:
            print("stunned")
            self.image = self.Bossdash3.copy()
            self.xSpeed = self.ySpeed = 0
            if self.tempframe >= 45:
                self.status = 1
                self.tempframe = 0
        #移動
        if self.status == 1:
            print("moving")
            self.image = self.BossMove[(self.frame % 14)].copy()
            self.processMove(MC)
        #攻擊
        if self.status == 2:
            print("atk")
            self.image = self.Bossattack.copy()
            self.doattack()
        #衝刺
        if self.status == 3:
            print("dash")
            self.dash()
        if self.faceDir:
            self.image = pygame.transform.flip(self.image, True, False)
        
        for each in wallGroup:
            if abs(each.center[0] - self.center[0]) > 350 and abs(each.center[1] - self.center[1]) > 240:
                continue
            if self.rect.colliderect(each.rect):
                if self.status == 3:
                    self.status = -1
                    self.xSpeed = 0
                    self.tempframe = 0
                if self.ySpeed < 0 and (self.y - each.bottom) >= self.ySpeed:
                    self.y = each.bottom
                    self.ySpeed = 0-int(self.ySpeed/4)
                elif self.ySpeed > 0 and (self.bottom - each.y) <= self.ySpeed:
                    self.y = each.y - self.height
                    self.ySpeed = 0
            if self.rect.colliderect(each.rect):
                if (self.x - each.right) >= self.xSpeed:
                    self.x = each.right
                    self.xSpeed = 0
                elif (self.right - each.x) <= self.xSpeed:
                    self.x = each.x - self.width
                    self.xSpeed = 0
                self.fix_pos("border")
            self.fix_pos("border")
        
        self.fix_pos("border")
        
        # Check if on ground
        tempRect = pygame.Rect(self.x, self.bottom, self.width, 1)
        for each in wallGroup:
            if abs(each.center[0] - self.center[0]) > 350 and abs(each.center[1] - self.center[1]) > 240:
                continue
            if pygame.Rect(0, self.bottom, self.max_x+self.width, 1).colliderect(each.rect) and not tempRect.colliderect(each.rect):
                self.onGround = False
            if tempRect.colliderect(each.rect) and self.ySpeed >= 0:
                self.onGround = True
                self.ySpeed = 0
                break
        
        if not self.onGround:
            self.ySpeed += 4
        
        if self.jumpCooldown:
            self.jumpCooldown -= 1
        if self.skillCooldown:
            self.skillCooldown -= 1
        if self.attackCooldown:
            self.attackCooldown -= 1

        #更新攻擊
        for each in self.attack:
            each.update(self)
        #檢測死亡
        if self.health <= 0:
            self.status = 0
        
        print("", end = "\n\n")
    
    def drawSelf(self, mapImage):
        for each in self.attack:
            mapImage.blit(each.image, [each.x, each.y])
        # print(self.image)
        # self.image.fill(255, 255, 255)
        mapImage.blit(self.image, [self.x, self.y])
    
    def fix_pos(self, txt = "border"):
        txt = txt.lower()
        if txt == "xy":
            self.right = self.x + self.width
            self.bottom = self.y + self.height
            self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
            self.center = [self.x + self.width / 2, self.y + self.height / 2]
            return
        if txt == "rb":
            self.x = self.right - self.width
            self.y = self.bottom - self.height
            self.fix_pos("border")
            return
        if txt == "c":
            self.x = self.center[0] - self.width / 2
            self.y = self.center[1] - self.height / 2
            self.fix_pos("border")
            return
        if txt == "border":
            if self.x < 0:
                self.x = 0
                self.xSpeed = 0
            elif self.x > self.max_x:
                self.x = self.max_x
                self.xSpeed = 0
            if self.y < 0:
                self.y = 0
                self.ySpeed = int(abs(self.ySpeed)/4)
            elif self.y > self.max_y:
                self.y = self.max_y
                self.ySpeed = 0
                self.onGround = True
            self.fix_pos("xy")
    
    def find_higher_wall(self, wallObj, wallGroup, get_all = False):
        x, y = wallObj.pos
        higher_wall_list = []
        for each in wallGroup:
            if each.pos[1] == y and each.pos[0] < x:
                higher_wall_list.append(each)
                if not get_all:
                    break
        return each


class Attack(pygame.sprite.Sprite):

    def __init__(self, boss):
        pygame.sprite.Sprite.__init__(self)

        self.picture  = []
        for count in range(1, 6):
            self.picture.append(pygame.image.load("image\\boss attack\\boss attack{0}.png".format(str(count))))

        self.boss = boss
        self.move = [boss.faceDir*400-100, 0]
        self.x = boss.x + self.move[0]
        self.y = boss.y + self.move[1]
        self.width = 100
        self.height = 200
        self.faceDir = boss.faceDir
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(pygame.Color(255, 0, 0))
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.timer = 5
    
    def update(self, boss):
        if self.timer:
            self.x = boss.x + self.move[0]
            self.y = boss.y + self.move[1]
            self.rect = self.image.get_rect(topleft=(self.x, self.y))
            self.timer -= 1
            self.image = self.picture[self.timer].copy()
            self.image.set_colorkey((0, 255, 0))
            return True
        self.kill()
        return False





