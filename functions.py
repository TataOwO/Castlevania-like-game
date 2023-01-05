import pygame

heart_image = pygame.image.load("image\\heart.png")
heart_image.set_colorkey([14, 209, 69])

stopping_image = pygame.image.load("image\\stopping.png")

#畫血條
def draw_health(screen, hp, x, y):
    wide = 45
    length = 35
    bar_LENGTH = 200
    bar_HEIGHT = 40
    bar = int(hp*bar_LENGTH/100)
    bar_rect = pygame.Rect(x, y, bar, bar_HEIGHT)
    #screen.blit(heart_image, [x-50, y+2])
    temp = 0
    while hp > 20:
        screen.blit(heart_image, [x+wide*temp, y])
        temp += 1
        hp -= 20
    if hp:
        gap = hp*2
        screen.blit(pygame.transform.scale(heart_image, [gap, gap]), [x+20-hp+wide*temp, y+20-hp])
    #0~20死亡(未寫)


    #pygame.draw.rect(screen, (172,50,50), bar_rect)

#畫字
def draw_text(screen, text, size, x, y, color):
    font = pygame.font.SysFont("segoe-ui-symbol.ttf", size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, [x, y])

#畫劇本
def draw_dialog(screen, text, size):
    font = pygame.font.SysFont("segoe-ui-symbol.ttf", size)
    dialog = font.render(text, True, pygame.Color(0, 0, 0))
    pygame.draw.rect(screen, pygame.Color(255, 255, 255), [20, 480, 1240, 200], 0) #最後一個0等於實心
    screen.blit(dialog, [50, 540])

#畫開投文字
def draw_BeginStence(screen, color):

    #標題
    draw_text(screen, "The Hopeless Jailbreak", 120, 100, 75, pygame.Color(255, 0, 0))

    #操作
    draw_text(screen, "press", 100, 50, 330, color)
    draw_text(screen, "to", 100, 320, 330, color)
    draw_text(screen, " A            go left", 60, 240, 220, color)
    draw_text(screen, " D            go right", 60, 240, 280, color)
    draw_text(screen, " W            jump", 60, 240, 340, color)
    draw_text(screen, " S            interact", 60, 240, 400, color)
    draw_text(screen, " E            stop", 60, 240, 460, color)
    draw_text(screen, "ESC          close the game", 60, 220, 520, color)
   
#畫暫停
def draw_stopping(screen, x, y):
    screen.blit(stopping_image, [x-200, y-90])

"""
#模糊效果
def blur_image(surface, r = 10):
    cvImg = pygame.surfarray.array3d(surface.copy())
    cvImg = cvImg.transpose([1, 0, 2])
    blur = cv2.blur(cvImg, (r, r))
    blur = numpy.rot90(cv2.flip(blur, 1, blur))
    pygBlur = pygame.surfarray.make_surface(blur)
    return pygBlur
"""

    







    
