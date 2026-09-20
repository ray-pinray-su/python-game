######################匯入模組######################
import pygame
import sys

######################初始化######################
pygame.init()  # 啟動pygame
width = 640  # 設定寬度
height = 320  # 設定高度
######################建立視窗及物件######################
# 設定視窗大小
screen = pygame.display.set_mode((width, height))
# 設定視窗標題
pygame.display.set_caption("game")
######################建立畫布######################
bg = pygame.Surface((width, height))  # 建立畫布
bg.fill((120, 255, 200))  # 設定畫布顏色
######################繪製圓形######################
# 畫圓形,(畫布,顏色,圓心座標,半徑,線寬)
pygame.draw.circle(bg, (0, 0, 255), (200, 100), 30, 0)
pygame.draw.circle(bg, (0, 0, 255), (400, 100), 30, 0)

# 畫矩形,(畫布,顏色,[x,y,寬,高],線寬)
pygame.draw.rect(bg, (0, 255, 0), [270, 130, 60, 40], 5)

# 畫橢圓,(畫布,顏色,[x,y,寬,高],線寬)
pygame.draw.ellipse(bg, (255, 0, 0), [130, 160, 60, 35], 5)
pygame.draw.ellipse(bg, (255, 0, 0), [400, 160, 60, 35], 5)
# 畫線,(畫布,顏色,起點座標,終點座標,線寬)
pygame.draw.line(bg, (255, 0, 255), (240, 220), (360, 220), 3)
######################循環偵測######################
while True:
    x, y = pygame.mouse.get_pos()  # 取得滑鼠座標
    for event in pygame.event.get():  # 偵測事件
        if event.type == pygame.QUIT:  # 偵測到關閉視窗
            sys.exit()  # 結束程式
    screen.blit(bg, (0, 0))  # 畫布貼到視窗上
    pygame.display.update()  # 更新視窗
    if event.type == pygame.MOUSEBUTTONDOWN:  # 偵測到滑鼠按下
        print("click")
        print("滑鼠座標:", x, y)  # 印出滑鼠座標
