import pygame
import functions
import living
import map
from boss import Boss

pygame.init()

def main(return_code):
    
    m_item = map.Item()
    m_NPC = None

    # setup
    resolution = (1280, 720)
    screen = pygame.display.set_mode(resolution, pygame.FULLSCREEN)
    #screen2 = screen.covert_alpha()
    pygame.display.set_caption("Castlevania")
    # blurred_screen = pygame.Surface(resolution)

    pygame.mouse.set_visible(False)
    
    blocks = pygame.sprite.Group()
    teleporterGroup = pygame.sprite.Group()
    enemyGroup = pygame.sprite.Group()
    bossGroup = pygame.sprite.Group()
    chestGroup = pygame.sprite.Group()
    
    # Creates a map
    # central_room kitchen_room bossroom basement starter_room
    mapD = map.Map(blocks, enemyGroup, teleporterGroup, chestGroup, "starter_room")
    if mapD.name == "bossroom":
        bossGroup.add(Boss(mapD))
    if mapD.name == "central_room":
        m_NPC = map.NPC()
    
    GREY = pygame.Color(128, 128, 128)
    WHITE = pygame.Color(255, 255, 255)
    
    frame = pygame.time.Clock()
    
    # Creates MC object
    MC = living.MainCharacter(mapD)
    
    running = True
    screen_action = 1 #Type 0 = 關閉遊戲, 1 = 遊戲初始, 2 = 主遊戲, 3 = 暫停, 4 = 結束遊戲, 5 = 對話框
    pause_cooldown = 0
    #劇本
    dialog_cooldown = 0
    dialog = 0
    text = ""
    with open("opera.txt", "r", encoding="utf-8") as fp:
        text = fp.read()
    dialog_stences = text.split("\n")
    del text
    sparklecooldown = 15
    sparklecooldown_switch = 1

    while screen_action:
        
        key_pressed = pygame.key.get_pressed()
        #開始畫面
        if screen_action == 1:

            screen.fill(GREY)
            
            #普通字
            functions.draw_BeginStence(screen, WHITE)
            
            #閃爍字
            sparklecooldown += sparklecooldown_switch
            if sparklecooldown < 0:
                sparklecooldown_switch = 1
            elif sparklecooldown > 15:
                sparklecooldown_switch = -1
            if sparklecooldown_switch == 1:
                functions.draw_text(screen, "press space to start", 60, 460, 620, WHITE)
            #開始遊戲
            if key_pressed[pygame.K_SPACE]:
                screen_action = 2
            #tick
            pygame.display.flip()
            frame.tick(30)

        #主遊戲
        if screen_action == 2:
            
            # Do certain action if pressed certain key(s)
            #移動
            if key_pressed[pygame.K_a]:
                MC.move(0)
            elif key_pressed[pygame.K_d]:
                MC.move(2)
            if key_pressed[pygame.K_w] or key_pressed[pygame.K_SPACE]:
                MC.move(1)
            
            for event in pygame.event.get():
            
                if event.type == pygame.QUIT:
                    return_code = screen_action
                    screen_action = 0 # Close
                
                elif event.type == pygame.KEYDOWN:
                    key_pressed = pygame.key.get_pressed()
                    #攻擊
                    if key_pressed[pygame.K_j] and not MC.attackCooldown:
                        MC.attack.add(living.Attack(MC, 0))
                        MC.image = MC.ChrAttack.copy()
                    #技能
                    if key_pressed[pygame.K_k] and not MC.attack2Cooldown and MC.skill_switch:
                        MC.attack2.add(living.Attack2(MC, 0))
                        MC.image = MC.ChrAttack.copy()
                    #互動
                    if key_pressed[pygame.K_s]:
                    
                        # 宝箱开启
                        chestGroup.update(MC)
                            
                        # 傳送門使用
                        teleported = False
                        for each in teleporterGroup:
                            teleported = each.check(MC, mapD.name)
                            if teleported:
                                mapD = map.Map(blocks, enemyGroup, teleporterGroup, chestGroup, teleported[0], teleported[1])
                                MC.x, MC.y = mapD.MC_pos
                                MC.tempy = MC.y
                                MC.max_x = mapD.width - MC.width
                                MC.max_y = mapD.height - MC.height
                                MC.onGround = False
                                if mapD.name == "bossroom":
                                    boss_exist = False
                                    for each in bossGroup:
                                        boss_exist = True
                                        break
                                    if not boss_exist:
                                        bossGroup.add(Boss(mapD))
                                if mapD.name == "central_room":
                                    m_NPC = map.NPC()
                                else:
                                    m_NPC = None
                        
                        # NPC對話
                        if m_NPC and dialog_cooldown >= 30 and m_NPC.rect.colliderect(MC.rect) and not MC.skill_switch:
                            dialog_cooldown = 0
                            screen_action = 5
                            MC.skill_switch = 1
                        
                    #使用道具            
                    if key_pressed[pygame.K_f]:
                        if MC.food > 0:
                            if MC.health >= 100:
                                MC.health = 100
                            else:
                                MC.health += 20
                                MC.food -= 1
                    #結束遊戲
                    if key_pressed[pygame.K_ESCAPE]:
                        if screen_action == 2:
                            return_code = False
                            screen_action = 0
                    
                    #暫停
                    if key_pressed[pygame.K_e] and pause_cooldown >= 30:
                        pause_cooldown = 0
                        screen_action = 3
                        # blurred_screen = functions.blur_image(screen)
                        continue
            
            if dialog_cooldown <=30:
                dialog_cooldown +=1
            
            #暫停冷卻
            if pause_cooldown <= 30:
                pause_cooldown += 1
            
            #更新主角
            MC.update(blocks, enemyGroup, bossGroup)
            
            #更新敵人
            for enemy in enemyGroup:
                enemy.update(blocks, MC)
            for each in bossGroup:
                each.update(MC, blocks)

            # Draw screen
            #畫背景
            mapD.image.blit(mapD.default_image, [0, 0])
            
            #畫boss
            for each in bossGroup:
                each.drawSelf(mapD.image)
            
            #畫主角
            mapD.image.blit(MC.image, MC.imagePos)

            #畫攻擊
            for each in MC.attack:
                mapD.image.blit(each.image, [each.x, each.y])
            #畫技能
            for each in MC.attack2:
                mapD.image.blit(each.image, [each.x, each.y])
                each.update(blocks)
            #畫牆壁跟框
            # blocks.draw(mapD.image)
            screen.fill(GREY)

            #畫箱子
            for each in chestGroup:
                mapD.image.blit(each.image, [each.x, each.y])
            
            #畫NPC
            if m_NPC:
                mapD.image.blit(m_NPC.image, [m_NPC.x, m_NPC.y])
            #畫敵人
            for Enemy in enemyGroup:
                mapD.image.blit(Enemy.image, [Enemy.x, Enemy.y])
            
            boss_exist = False
            for each in bossGroup:
                boss_exist = True
                if each.status == 0:
                    screen_action = 4
            if boss_exist:
                screen.blit(mapD.image, [0, 0])
            else:
                screenx = MC.x - 610
                screeny = MC.tempy - 400
                if screenx < 0:
                    screenx = 0
                elif screenx > mapD.width - resolution[0]:
                    screenx = mapD.width - resolution[0]
                if screeny < 0:
                    screeny = 0
                elif screeny > mapD.height - resolution[1]:
                    screeny = mapD.height - resolution[1]
                if mapD.height < resolution[1]:
                    screeny = mapD.height - resolution[1]
                # opt_scr = mapD.image.subsurface(pygame.Rect([screenx, screeny], resolution))
                # screen.blit(opt_scr, [0, 0])
                screen.blit(mapD.image, [-screenx, -screeny])
            #畫血條
            functions.draw_health(screen, MC.health, 80, 50)
            #死亡
            if MC.health <20:
                screen_action = 4
            #畫食物跟數字
            m_item.drawSelf(screen, MC)

            # tick
            pygame.display.flip()
            frame.tick(30)
            continue
        
        #暫停
        if screen_action == 3:
            #暫停冷卻
            if pause_cooldown <=30:
                pause_cooldown+=1
            #回到遊戲
            if key_pressed[pygame.K_e] and pause_cooldown >=30:
                pause_cooldown = 0
                screen_action = 2
            
            #模糊背景
            # screen.blit(blurred_screen, [0, 0])
            #畫暫停畫面
            functions.draw_stopping(screen, 640, 360)
            #tick
            pygame.display.flip()
            frame.tick(30)

        #結束
        if screen_action == 4:
            #死亡畫面
            if MC.health <= 0:
                screen.fill(GREY)
                functions.draw_text(screen, "~~YOU DIED~~", 100, 396, 320, WHITE)
                functions.draw_text(screen, "press ESC to quit the game", 50, 417, 410, WHITE)
                functions.draw_text(screen, "press Space to relive", 50, 467, 460, WHITE)
                #復活
                if key_pressed[pygame.K_SPACE]:
                    screen_action = 0
                    return_code = 1
            else: # 遊戲結束
                screen.fill(GREY)
                functions.draw_text(screen, "~~YOU ESCAPED~~", 100, 311, 335, WHITE)
                functions.draw_text(screen, "press ESC to quit the game", 50, 417, 415, WHITE)
            
            #tick
            pygame.display.flip()
            frame.tick(30)
        
        #對話框狀態
        if screen_action == 5:
            #畫對話框
            functions.draw_dialog(screen, dialog_stences[dialog], 60)
            #print(dialog)
            #對話冷卻
            if dialog_cooldown <30:
                dialog_cooldown +=1
            #下一句話
            if key_pressed[pygame.K_s] and dialog_cooldown >= 30:
                dialog +=1
                dialog_cooldown = 0
            #結束對話
            if dialog == 8:
                screen_action = 2
                dialog_cooldown = 0
            
            #tick
            pygame.display.flip()
            frame.tick(30)

        #結束遊戲
        for event in pygame.event.get():
            if event.type == pygame.QUIT or key_pressed[pygame.K_ESCAPE]:
                return_code = False
                screen_action = 0 # Close

    return return_code
        

if __name__ == "__main__":
    return_code = True
    while return_code:
        return_code = main(return_code)
    pygame.quit()


