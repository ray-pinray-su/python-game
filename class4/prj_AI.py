######################載入套件######################
import pygame  # 載入pygame套件
import sys  # 載入sys套件
import random  # 載入random套件
import math


######################物件類別######################
class Brick:
    def __init__(self, x, y, width, height, color, is_special=False):
        """
        初始化磚塊/Initialize the brick\n
        x,y:磚塊左上角座標/Top-left corner coordinates of the brick\n
        width,height:磚塊的寬,高/Width and height of the brick\n
        color:磚塊的顏色/Color of the brick
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hit = False
        self.is_special = is_special
        self.spawn_balls = False

    def draw(self, display_area):
        """
        繪製磚塊/Draw the brick\n
        display_area:繪製磚塊的區域/Drawing area\n
        """
        if not self.hit:
            pygame.draw.rect(display_area, self.color, self.rect)
            if self.is_special:
                pygame.draw.rect(display_area, (255, 215, 0), self.rect, 3)


class Ball:
    def __init__(self, x, y, radius, color, speed_x, speed_y):
        """
        初始化球/Initialize the ball\n
        x,y:球的中心座標/Center coordinates of the ball\n
        radius:球的半徑/Radius of the ball\n
        color:球的顏色/Color of the ball
        speed_x,speed_y:球的初始速度分量/Initial horizontal and vertical speed
        """
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.initial_speed_x = speed_x
        self.initial_speed_y = speed_y
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.is_moving = False
        self.is_lost = False
        self.start_offset = 0

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
            self.is_lost = True
            return 0

        if (
            pad.rect.y <= self.y + self.radius <= pad.rect.y + pad.rect.height
            and pad.rect.x <= self.x <= pad.rect.x + pad.rect.width
        ):
            self.speed_y = -abs(self.speed_y)

        score = 0
        for brick in bricks:
            if not brick.hit:
                dx = abs(self.x - (brick.rect.x + brick.rect.width / 2))
                dy = abs(self.y - (brick.rect.y + brick.rect.height / 2))
                if dx <= (self.radius + brick.rect.width / 2) and dy <= (
                    self.radius + brick.rect.height / 2
                ):
                    brick.hit = True
                    score += 1
                    if brick.is_special:
                        brick.spawn_balls = True

                    if (
                        self.x < brick.rect.x
                        or self.x > brick.rect.x + brick.rect.width
                    ):
                        self.speed_x = -self.speed_x
                    else:
                        self.speed_y = -self.speed_y

        return score


######################定義函式區######################
def create_bricks():
    """建立磚塊清單，開始新遊戲時可以重新呼叫。"""
    new_bricks = []
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
            new_bricks.append(brick)
    special_bricks = random.sample(range(len(new_bricks)), 8)
    for special_brick in special_bricks:
        new_bricks[special_brick].is_special = True
    return new_bricks


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
font = pygame.font.SysFont("Microsoft JhengHei", 28)
large_font = pygame.font.SysFont("Microsoft JhengHei", 44)
######################磚塊設定######################
bricks_row = 9
bricks_col = 11
brick_w = 58
brick_h = 16
brick_gap = 2
bricks = create_bricks()

######################顯示文字設定######################

######################底板設定######################
pad = Brick(0, bg_y - 48, brick_w, brick_h, (255, 255, 255))
######################球設定######################
Ball_radius = 10
Ball_color = (255, 215, 0)
ball = Ball(
    pad.rect.x + pad.rect.width // 2,
    pad.rect.y - Ball_radius,
    Ball_radius,
    Ball_color,
    4.5 * math.cos(math.radians(45)),
    -4.5 * math.sin(math.radians(45)),
)
ball.start_offset = -Ball_radius - 5
ball2 = Ball(
    pad.rect.x + pad.rect.width // 2,
    pad.rect.y - Ball_radius,
    Ball_radius,
    (100, 200, 255),
    -5.5 * math.cos(math.radians(60)),
    -5.5 * math.sin(math.radians(60)),
)
ball2.start_offset = 0
ball3 = Ball(
    pad.rect.x + pad.rect.width // 2,
    pad.rect.y - Ball_radius,
    Ball_radius,
    (180, 100, 255),
    4.5 * math.cos(math.radians(45)),
    -4.5 * math.sin(math.radians(45)),
)
ball3.start_offset = Ball_radius + 5
balls = [ball, ball2, ball3]
score = 0
high_score = 0
game_over = False
game_result = ""
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

    if not game_over:
        new_balls = []
        for current_ball in balls:
            if current_ball.is_lost:
                continue
            if not current_ball.is_moving:
                current_ball.x = (
                    pad.rect.x + pad.rect.width // 2 + current_ball.start_offset
                )
                current_ball.y = pad.rect.y - current_ball.radius
            else:
                current_ball.move()
                score += current_ball.check_collision(bg_x, bg_y, pad, bricks)
                for brick in bricks:
                    if brick.spawn_balls:
                        brick.spawn_balls = False
                        spawn_speeds = [-3, 0, 3]
                        spawn_colors = [
                            (255, 100, 100),
                            (100, 255, 150),
                            (255, 255, 100),
                        ]
                        for index in range(3):
                            new_ball = Ball(
                                brick.rect.centerx,
                                brick.rect.centery,
                                Ball_radius,
                                spawn_colors[index],
                                spawn_speeds[index],
                                -3.5,
                            )
                            new_ball.is_moving = True
                            new_balls.append(new_ball)

        balls.extend(new_balls)

        remaining_bricks = 0
        for brick in bricks:
            if not brick.hit:
                remaining_bricks += 1

        remaining_balls = 0
        for current_ball in balls:
            if not current_ball.is_lost:
                remaining_balls += 1

        if remaining_bricks == 0:
            game_over = True
            game_result = "你贏了！"
        elif remaining_balls == 0:
            game_over = True
            game_result = "遊戲結束！"

    if score > high_score:
        high_score = score

    for event in pygame.event.get():  # 偵測事件
        if event.type == pygame.QUIT:  # 偵測到關閉視窗
            sys.exit()  # 結束程式
        if event.type == pygame.MOUSEBUTTONDOWN:  # 偵測到滑鼠按下
            if game_over:
                bricks = create_bricks()
                balls = [ball, ball2, ball3]
                score = 0
                game_over = False
                game_result = ""
                for current_ball in balls:
                    current_ball.is_moving = False
                    current_ball.is_lost = False
                    current_ball.speed_x = current_ball.initial_speed_x
                    current_ball.speed_y = current_ball.initial_speed_y
                    current_ball.x = (
                        pad.rect.x + pad.rect.width // 2 + current_ball.start_offset
                    )
                    current_ball.y = pad.rect.y - current_ball.radius
            else:
                for current_ball in balls:
                    if not current_ball.is_lost:
                        current_ball.is_moving = True  # 開始移動球

    for brick in bricks:
        brick.draw(screen)

    pad.draw(screen)  # 繪製底板
    for current_ball in balls:
        if not current_ball.is_lost:
            current_ball.draw(screen)  # 繪製球

    score_text = font.render("分數：" + str(score), True, (255, 255, 255))
    screen.blit(score_text, (10, 10))
    high_score_text = font.render(
        "最高分：" + str(high_score), True, (255, 255, 255)
    )
    screen.blit(high_score_text, (bg_x - 180, 10))

    if game_over:
        result_text = large_font.render(game_result, True, (255, 255, 255))
        result_rect = result_text.get_rect(center=(bg_x // 2, bg_y // 2 - 35))
        screen.blit(result_text, result_rect)
        final_score_text = font.render("最後分數：" + str(score), True, (255, 255, 255))
        final_score_rect = final_score_text.get_rect(center=(bg_x // 2, bg_y // 2 + 15))
        screen.blit(final_score_text, final_score_rect)
        restart_text = font.render("點擊滑鼠重新開始", True, (255, 255, 255))
        restart_rect = restart_text.get_rect(center=(bg_x // 2, bg_y // 2 + 60))
        screen.blit(restart_text, restart_rect)

    pygame.display.update()  # 更新視窗
