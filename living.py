from numpy import e
import pygame


#主角
class MainCharacter(pygame.sprite.Sprite):
    def __init__(self, mapD):
        pygame.sprite.Sprite.__init__(self)
        
        data = mapD.DATA["living"]["MC"]
        # Shows different images when doing different actions
        self.ChrStand = pygame.image.load("image\\MC\\soul2.png")
        #self.ChrJump  = pygame.image.load("image\\MC\\soul6.png")
        self.ChrJump = pygame.image.load("image\\souljump.png")
        self.ChrAttack = pygame.image.load("image\\MCattack\\soulattack5.png")
        
        self.ChrMove  = []
        for count in range(1, 16):
            self.ChrMove.append(pygame.image.load("image\\MC\\soul{0}.png".format(str(count))))
            # self.ChrMove.append(pygame.Surface([60, 100]))
        
        self.image = self.ChrJump.copy()
        
        self.frame = 0
        
        self.imagePos = [0, 0]
        self.width = data["size"][0]*20
        self.height = data["size"][1]*20
        self.x, self.y = mapD.MC_pos
        self.center = [self.x+self.width/2, self.y+self.height/2]
        self.right = self.x + self.width
        self.bottom = self.y + self.height
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.max_x = mapD.width-self.width
        self.max_y = mapD.height-self.height
        self.tempy = self.y # Used to fix map position
        self.faceDir = 0 # Determine which direction MC is facing at
        self.onGround = False
        self.attackCooldown = False
        self.attack2Cooldown = False
        self.xSpeed = 0
        self.ySpeed = 0
        self.health = 100
        self.injure = 30
        self.attack = pygame.sprite.Group()
        self.attack2 = pygame.sprite.Group()
        self.food = 0
        self.key_1 = 0
        self.key_2 = 0
        self.skill_switch = 0
    
    def move(self, moveDir):
        if moveDir == 0: # Goes left
            self.xSpeed = -10
            self.faceDir = 0
        elif moveDir == 1 and self.onGround: # Jump
            self.ySpeed = -40
            self.onGround = False
        elif moveDir == 2: # Goes right
            self.xSpeed = 10
            self.faceDir = 1
    
    def update(self, wallGroup,enemyGroup, bossGroup):
        self.x += self.xSpeed
        self.y += self.ySpeed
        self.frame = (self.frame + 1)%15
        
        # Fix position (by map)
        if self.y > self.max_y:
            self.y = self.max_y
            self.ySpeed = 0
            self.onGround = True
        elif self.y < 0:
            self.y = 0
            self.ySpeed = 0-int(self.ySpeed/2)
        if self.x > self.max_x:
            self.x = self.max_x
            self.xSpeed = 0
        elif self.x < 0:
            self.x = 0
            self.xSpeed = 0
        self._fix_pos()
        
        # Fix position (by wall)
        for each in wallGroup:
            if abs(each.center[0] - self.center[0]) > 120 or abs(each.center[1] - self.center[1]) > 120:
                continue
            if self.rect.colliderect(each.rect) and self.xSpeed:
                fixed = True
                if self.onGround and each.bottom == self.bottom:
                    tempy = self.y
                    self.y = each.y - self.height
                    if self.y < 0:
                        self.y = tempy
                    fixed = False
                    self._fix_pos()
                    if pygame.sprite.spritecollide(self, wallGroup, False):
                        self.y = tempy
                        fixed = True
                if (self.x - each.right) >= self.xSpeed and fixed:
                    self.x = each.right
                    self.xSpeed = 0
                elif (self.right - each.x) <= self.xSpeed and fixed:
                    self.x = each.x - self.width
                    self.xSpeed = 0
                self._fix_pos()
            if self.rect.colliderect(each.rect):
                if (self.y - each.bottom) >= self.ySpeed and self.ySpeed < 0:
                    self.y = each.bottom
                    # self.y = prevy
                    self.ySpeed = 0-int(self.ySpeed/4)
                elif (self.bottom - each.y) <= self.ySpeed and self.ySpeed > 0:
                    self.y = each.y - self.height
                    # self.ySpeed = 0
            self._fix_pos()
        
        tempRect = pygame.Rect(self.x, self.bottom, self.width, 1)
        # Check if on ground
        for each in wallGroup:
            if abs(each.center[0] - self.center[0]) > 120 or abs(each.center[1] - self.center[1]) > 120:
                continue
            if pygame.Rect(0, self.bottom, self.max_x+self.width, 1).colliderect(each.rect) and not tempRect.colliderect(each.rect):
                self.onGround = False
            if tempRect.colliderect(each.rect) and self.ySpeed >= 0:
                self.onGround = True
                self.ySpeed = 0
                break
        
        if self.y >= self.max_y:
            self.y = self.max_y
            self.ySpeed = 0
            self.onGround = True
            self._fix_pos()
        
        # if on ground
        if self.onGround:
            self.tempy = self.y-int((self.y-self.tempy)*7/8)
            if self.xSpeed:
                self.image = self.ChrMove[self.frame].copy()
                self.imagePos = [self.x-0, self.y-0]
            else:
                self.image = self.ChrStand.copy()
                self.imagePos = [self.x-0, self.y-0]
            self.xSpeed = 0
        else:
            if self.tempy-self.y > 250:
                self.tempy = self.y + 250
            elif self.tempy-self.y < -150:
                self.tempy = self.y - 150
            self.imagePos = [self.x+0, self.y+0]
            self.image = self.ChrJump.copy()
            self.ySpeed += 4
        
        if not self.faceDir:
            self.image = pygame.transform.flip(self.image, True, False)
        
        self._fix_pos()
        #攻擊冷卻
        if self.attackCooldown:
            self.attackCooldown -= 1
        if self.attack2Cooldown:
            self.attack2Cooldown -= 1
        for each in self.attack:
            each.update(self)
        
        #injure
        if self.injure<30:
            self.injure += 1

        #主角受傷
        boss_exist = False
        for each in bossGroup:
            boss_exist = True
        collidedEnemy = pygame.sprite.spritecollide(self, enemyGroup, False)
        collidedBoss = []
        collidedBoss_attack = []
        boss = None
        if boss_exist:
            boss = [x for x in bossGroup][0]
            collidedBoss = pygame.sprite.spritecollide(self, bossGroup, False)
            collidedBoss_attack = pygame.sprite.spritecollide(self, boss.attack, False)
        
        if self.injure >=30 and (collidedEnemy or collidedBoss or collidedBoss_attack):
            self.injure = 0
            self.health -=20
            self.ySpeed -= 8
            self.onGround = False
        
        if collidedEnemy:
            
            if self.center[0]-collidedEnemy[0].center[0] > 0:
                self.xSpeed += 8
                self._fix_pos()
            else:
                self.xSpeed -= 8
                self._fix_pos()
        
        if collidedBoss:
            if self.center[0]- boss.center[0] > 0:
                self.xSpeed += 8
                self._fix_pos()
            else:
                self.xSpeed -= 8
                self._fix_pos()
        
        if collidedBoss_attack:
            if self.center[0] - boss.center[0] > 0:
                self.xSpeed += 8
                self._fix_pos()
            else:
                self.xSpeed -= 8
                self._fix_pos()
        
            
    
    def _fix_pos(self):
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.right, self.bottom = self.x + self.width, self.y + self.height
        self.center = [self.x+self.width/2, self.y+self.height/2]


# Attack: rect = None when no attack, follows MC, do not change dir when MC changes dir
class Attack(pygame.sprite.Sprite):

    def __init__(self, MC, type):
        pygame.sprite.Sprite.__init__(self)
        
        self.picture  = []
        for count in range(1, 6):
            self.picture.append(pygame.image.load("image\\attack\\attack{0}.png".format(str(count))))
        MC.attackCooldown = 20
        self.exist = True
        self.type = type
        self.faceDir = MC.faceDir
        if self.faceDir:
            self.x = MC.x + 60 #60 是主角的寬
        else:
            self.x = MC.x - 90 #90 是自己的寬
        self.y = MC.y
        self.timer = 5
        self.image = self.picture[self.timer-1].copy()
        self.image.set_colorkey((2, 255, 24))
        self.rect = pygame.Rect(self.x, self.y, 90, 100)
        
    def update(self, MC):
        self.timer -= 1
        self.image = self.picture[self.timer].copy()
        self.image.set_colorkey((2, 255, 24))
        if self.timer < 0:
            self.exist = False
            self.kill()
            return False
        else:
            if self.faceDir:
                self.x = MC.x + 60
            else:
                self.x = MC.x - 90
            self.y = MC.y
            self.rect = pygame.Rect(self.x, self.y, 90, 100)
            return True


#技能
class Attack2(pygame.sprite.Sprite):

    def __init__(self, MC, type):
        pygame.sprite.Sprite.__init__(self)
        
        MC.attack2Cooldown = 30

        self.frame = 0
        self.picture = []
        for count in range(1, 6):
            self.picture.append(pygame.image.load("image\\skill\\attack2 {0}.png".format(str(count))))

        self.exist = True
        self.type = type
        self.faceDir = MC.faceDir
        self.x = MC.x - 60 + self.faceDir * 90
        self.y = MC.y
        self.rect = pygame.Rect(self.x, self.y, 90, 90)
        self.timer = 10
        self.image = self.picture[self.frame]
        self.image.set_colorkey((2, 255, 24))
        if not self.faceDir:
            self.image = pygame.transform.flip(self.image, True, False)
        self.xspeed = 30
        if self.faceDir == 0:
            self.xspeed*=-1
        
    def update(self, wallgroup):

        self.x += self.xspeed
        self.frame = (self.frame + 1)%5
        self.image = self.picture[self.frame].copy()
        self.image.set_colorkey((2, 255, 24))
        if not self.faceDir:
            self.image = pygame.transform.flip(self.image, True, False)

        for each in wallgroup:
            if self.rect.colliderect(each.rect):
                self.exist = False
                self.kill()
            else:
                self.rect = pygame.Rect(self.x, self.y, 90, 90)


#敵人
class Enemy1(pygame.sprite.Sprite):
    def __init__(self, mapD, patrolRange, index):
        pygame.sprite.Sprite.__init__(self)
        
        self.frame = 0
        self.picture  = []
        for count in range(1, 14):
            self.picture.append(pygame.image.load("image\\enemy\\enemy{0}.png".format(str(count))))
        
        enemy_data = mapD.DATA["living"]["enemy1"]
        self.width = enemy_data["size"][0]*20
        self.height = enemy_data["size"][1]*20
        self.x = enemy_data["X"][index]*20
        self.y = enemy_data["Y"][index]*20
        self.patrol_x = self.x #紀錄巡邏位置
        self.patrol_y = self.y #紀錄巡邏位置
        
        self.image = self.picture[self.frame].copy()
        self.center = [self.x+self.width/2, self.y+self.height/2]
        self.right = self.x + self.width
        self.bottom = self.y + self.height
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.max_x = mapD.width-self.width
        self.max_y = mapD.height-self.height
        self.tempy = self.y # Used to fix map position
        self.faceDir = 1 # Determine which direction MC is facing at 0=left 1=right
        self.onGround = False
        self.attackCooldown = 0
        self.xSpeed = 5
        self.ySpeed = 0
        self.health = 80
        self.attack = pygame.sprite.Group()
        self.cooldown = 30
        self.pos = patrolRange/2
        self.patrolRange = patrolRange
        self.injury = 30


    def update(self, wallGroup, aim):

        if abs(self.center[0] - aim.center[0]) > 700 or \
           abs(self.center[1] - aim.center[1]) > 450:
           return
        
        self.frame = (self.frame + 1)%13
        self.image = self.picture[self.frame].copy()
        if self.faceDir:
            self.image = pygame.transform.flip(self.image, True, False)

        #受傷
        if pygame.sprite.spritecollide(self, aim.attack, False):
            #if self.injury >= 30:
            self.health -=4
            #攻擊到敵人主角後飛
            aim.ySpeed -= 2
            aim.onGround = False
            if aim.center[0]-self.center[0] > 0:
                aim.xSpeed += 2
                aim._fix_pos()
            else:
                aim.xSpeed -= 2
                aim._fix_pos()
                #self.injury = 0
            #受傷退後
            if self.faceDir == 1:
                self.x -= 6
            elif self.faceDir == 0:
                self.x += 6
            self._fix_pos
        if pygame.sprite.spritecollide(self, aim.attack2, True):
            if self.injury >= 30:
                self.health -=40
                self.injury = 0

        #巡邏
        if abs(self.center[0]-aim.center[0]) < 400 and abs(self.center[1]-aim.center[1]) < 200:
        
            self.faceDir = ((aim.x - self.x) > 0)

            #偵測攻擊(未實裝)
            if abs(aim.x - self.x)<60:
                
                if not self.attackCooldown:
                    #print(1)
                    self.attack.add(Attack(self, 0))
                    for each in self.attack:
                        each.update(self)
            else:
                if self.faceDir == 1:
                    self.x += self.xSpeed
                elif self.faceDir == 0:
                    self.x -= self.xSpeed
        
        else:
            #回到巡邏位置
            if self.x > self.patrol_x + self.patrolRange:
                self.faceDir = 0
            elif self.x < self.patrol_x:
                self.faceDir = 1
            
            if self.faceDir:
                self.x += self.xSpeed
            else:
                self.x -= self.xSpeed
            self._fix_pos()
            
            #受傷
        if self.injury <30:
            self.injury +=1

        #敵人攻擊
        #if self.attackCooldown:
            #self.attackCooldown -= 1
        #for each in self.attack:
            #print(0)
            #each.update(self)
        if self.x > self.max_x:
            self.x = self.max_x
            self.faceDir = 0
        elif self.x < 0:
            self.x = 0
            self.faceDir = 1
        self._fix_pos()
        
        # Fix position (by wall)
        for each in wallGroup:
            if abs(self.center[0] - each.center[0]) > 120 or abs(self.center[1] - each.center[1]) > 120:
                continue
            if self.rect.colliderect(each.rect):
                if self.center[0] > each.center[0]:
                    self.x = each.right
                    self._fix_pos()
                else:
                    self.x = each.x - self.width
                    self._fix_pos()

        if self.health <= 0:
            self.kill()

    
    def _fix_pos(self):
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.right, self.bottom = self.x + self.width, self.y + self.height
        self.center = [self.x+self.width/2, self.y+self.height/2]

