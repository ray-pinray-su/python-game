######################載入套件######################
import pygame
import sys


######################物件類別######################
class Player:
    def __init__(self, x, y, width, height, color):
        """
        初始化主角/Initialize the player/n
        x,y: 主角的左上角座標/Top-left position/n
        width,height: 主角的寬度與高度/Player's width and height/n
        color: 主角的顏色(RGB格式)/Player's color(RGB)/n
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.speed = 5

    def draw(self, display_area):
        """
        繪製主角/Draw the player/n
        display_area: 繪製主角的目標視窗/n
        """
        pygame.draw.rect(display_area, self.color, self.rect)

    def move(self, direction, bg_x):
        """
        移動主角並處理穿牆效果/Move the wrap the player/n
        direction: 移動方向(1:向右/Right, -1:向左/Left)/Direction(1: right, -1: left)/n
        bg_x: 遊戲視窗的寬度, 用於判斷是否穿牆/Window width for wrapping/n
        """
        self.rect.x += direction * self.speed
        if self.rect.right < 0:
            self.rect.left = bg_x
        elif self.rect.left > bg_x:
            self.rect.right = 0


######################初始化設定######################
pygame.init()
FPS = pygame.time.Clock()
######################遊戲視窗設定######################
bg_x = 400
bg_y = 600
bg_size = (bg_x, bg_y)
pygame.display.set_caption("Doodle Jump")
screen = pygame.display.set_mode(bg_size)
######################主角設定######################
player_w = 30
player_h = 30
player_x = (bg_x - player_w) // 2
player_y = bg_y - player_h - 50
player = Player(player_x, player_y, player_w, player_h, (0, 255, 0))
######################主程式######################
while True:
    FPS.tick(60)
    screen.fill((0, 0, 0))

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        player.move(-1, bg_x)
    if keys[pygame.K_RIGHT]:
        player.move(1, bg_x)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    player.draw(screen)
    pygame.display.update()
