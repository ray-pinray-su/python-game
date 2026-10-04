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
        if not self.hit:
            pygame.draw.rect(display_area, self.color, self.rect)


class Ball:
    def __init__(self, x, y, radius, color):
        """
        初始化球/Initialize the ball\n
        x,y:球的中心座標/Center coordinates of the ball\n
        radius:球的半徑/Radius of the ball\n
        color:球的顏色/Color of the ball
        """
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.speed_x = 5
        self.speed_y = -5
        self.is_moving = False

    def draw(self, display_area):
        """
        繪製球/Draw the ball\n
        display_area:繪製球的區域/Drawing area\n
        """
        pygame.draw.circle(
            display_area, self.color, (int(self.x), int(self.y)), self.radius
        )

    def move(self):
        """
        移動球/Move the ball\n
        """
        if self.is_moving:
            self.x += self.speed_x
            self.y += self.speed_y

    def check_collision(self, bg_x, bg_y, pad, bricks):
        """
        檢查球的碰撞並處理反彈/Check collision and bounce\n
        bg_x,bg_y:遊戲視窗的寬,高/Width and height of the game window\n
        bricks:磚塊列表/List of bricks\n
        pad:底板物件/Pad object\n
        """
        if self.x - self.radius <= 0 or self.x + self.radius >= bg_x:
            self.speed_x = -self.speed_x

        if self.y - self.radius <= 0:
            self.speed_y = -self.speed_y

        if self.y + self.radius >= bg_y:
            self.is_moving = False

        if (
            pad.rect.y <= self.y + self.radius <= pad.rect.y + pad.rect.height
            and pad.rect.x <= self.x <= pad.rect.x + pad.rect.width
        ):
            self.speed_y = -abs(self.speed_y)

        for brick in bricks:
            if not brick.hit:
                dx = abs(self.x - (brick.rect.x + brick.rect.width / 2))
                dy = abs(self.y - (brick.rect.y + brick.rect.height / 2))
                if dx <= (self.radius + brick.rect.width / 2) and dy <= (
                    self.radius + brick.rect.height / 2
                ):
                    brick.hit = True

                    if (
                        self.x < brick.rect.x
                        or self.x > brick.rect.x + brick.rect.width
                    ):
                        self.speed_x = -self.speed_x
                    else:
                        self.speed_y = -self.speed_y


######################定義函式區######################

######################初始化設定######################
pygame.init()  # 啟動pygame
FPS = pygame.time.Clock()  # 設定遊戲更新速度
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
Ball_radius = 10
Ball_color = (255, 215, 0)
ball = Ball(
    pad.rect.x + pad.rect.width // 2, pad.rect.y - Ball_radius, Ball_radius, Ball_color
)
######################遊戲結束設定######################

######################主程式######################
while True:
    FPS.tick(60)  # 設定遊戲更新速度為60FPS
    screen.fill((0, 0, 0))  # 設定背景顏色
    mos_x, mos_y = pygame.mouse.get_pos()  # 取得滑鼠座標
    pad.rect.x = mos_x - pad.rect.width // 2  # 底板中心跟隨滑鼠移動

    if pad.rect.x < 0:  # 限制底板不超出左邊界
        pad.rect.x = 0

    if pad.rect.x > bg_x - pad.rect.width:  # 限制底板不超出右邊界
        pad.rect.x = bg_x - pad.rect.width

    if not ball.is_moving:
        ball.x = pad.rect.x + pad.rect.width // 2
        ball.y = pad.rect.y - ball.radius
    else:
        ball.move()
        ball.check_collision(bg_x, bg_y, pad, bricks)

    for event in pygame.event.get():  # 偵測事件
        if event.type == pygame.QUIT:  # 偵測到關閉視窗
            sys.exit()  # 結束程式
        if event.type == pygame.MOUSEBUTTONDOWN:  # 偵測到滑鼠按下
            if not ball.is_moving:
                ball.is_moving = True  # 開始移動球

    for brick in bricks:
        brick.draw(screen)
        pad.draw(screen)  # 繪製底板
        ball.draw(screen)  # 繪製球
    pygame.display.update()  # 更新視窗
