######################載入套件######################
import pygame  # 載入pygame套件
import sys  # 載入sys套件
import random  # 載入random套件


######################物件類別######################
class Brick:
    def __init__(self, x, y, width, height, color):
        """
        初始化磚塊/Initialize the brick\n
        x,y:磚塊左上角座標/Top-left corner coordinates of the brick\n
        width,height:磚塊的寬,高/Width and height of the brick\n
        color:磚塊的顏色/Color of the brick
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hit = False

    def draw(self, display_area):
        """
        繪製磚塊/Draw the brick\n
        display_area:繪製磚塊的區域/Drawing area\n
        """
        pygame.draw.rect(display_area, self.color, self.rect)


######################定義函式區######################

######################初始化設定######################
pygame.init()  # 啟動pygame
######################載入圖片######################

######################遊戲視窗設定######################
bg_x = 800
bg_y = 600
bg_size = (bg_x, bg_y)
pygame.display.set_caption("打磚塊")  # 設定視窗標題
screen = pygame.display.set_mode(bg_size)  # 設定視窗大小
######################磚塊設定######################
bricks_row = 9
bricks_col = 11
brick_w = 58
brick_h = 16
brick_gap = 2
bricks = []
for col in range(bricks_col):
    for row in range(bricks_row):
        x = col * (brick_w + brick_gap) + 70  # 從70開始排
        y = row * (brick_h + brick_gap) + 60  # 從60開始排
        color = (
            random.randint(30, 255),
            random.randint(30, 255),
            random.randint(30, 255),
        )
        brick = Brick(x, y, brick_w, brick_h, color)
        bricks.append(brick)
######################顯示文字設定######################

######################底板設定######################
pad = Brick(0, bg_y - 48, brick_w, brick_h, (255, 255, 255))
######################球設定######################

######################遊戲結束設定######################

######################主程式######################
while True:
    screen.fill((0, 0, 0))  # 設定背景顏色
    mos_x, mos_y = pygame.mouse.get_pos()  # 取得滑鼠座標
    pad.rect.x = mos_x - pad.rect.width // 2  # 底板中心跟隨滑鼠移動

    if pad.rect.x < 0:  # 限制底板不超出左邊界
        pad.rect.x = 0

    if pad.rect.x > bg_x - pad.rect.width:  # 限制底板不超出右邊界
        pad.rect.x = bg_x - pad.rect.width

    for event in pygame.event.get():  # 偵測事件
        if event.type == pygame.QUIT:  # 偵測到關閉視窗
            sys.exit()  # 結束程式

    for brick in bricks:
        brick.draw(screen)
        pad.draw(screen)  # 繪製底板
    pygame.display.update()  # 更新視窗
