######################載入套件######################
import pygame  # 載入pygame套件
import sys  # 載入sys套件
import random  # 載入random套件
import math
import struct


######################物件類別######################
class Brick:
    def __init__(self, x, y, width, height, color, is_special=False, is_reversal=False):
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
        self.is_reversal = is_reversal
        self.spawn_balls = False
        self.reverse_balls = False

    def draw(self, display_area):
        """
        繪製磚塊/Draw the brick\n
        display_area:繪製磚塊的區域/Drawing area\n
        """
        if not self.hit:
            pygame.draw.rect(display_area, self.color, self.rect)
            if self.is_special:
                pygame.draw.rect(display_area, (255, 215, 0), self.rect, 3)
            elif self.is_reversal:
                pygame.draw.rect(display_area, (0, 255, 255), self.rect, 3)


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
        self.last_event = ""

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
        self.last_event = ""
        if self.x - self.radius <= 0 or self.x + self.radius >= bg_x:
            self.speed_x = -self.speed_x
            self.last_event = "wall"

        if self.y - self.radius <= 0:
            self.speed_y = -self.speed_y
            self.last_event = "wall"

        if self.y + self.radius >= bg_y:
            self.is_moving = False
            self.is_lost = True
            self.last_event = "lost"
            return 0

        if (
            pad.rect.y <= self.y + self.radius <= pad.rect.y + pad.rect.height
            and pad.rect.x <= self.x <= pad.rect.x + pad.rect.width
        ):
            self.speed_y = -abs(self.speed_y)
            self.last_event = "pad"

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
                    self.last_event = "brick"
                    if brick.is_special:
                        brick.spawn_balls = True
                    if brick.is_reversal:
                        brick.reverse_balls = True

                    if not brick.is_reversal:
                        if (
                            self.x < brick.rect.x
                            or self.x > brick.rect.x + brick.rect.width
                        ):
                            self.speed_x = -self.speed_x
                        else:
                            self.speed_y = -self.speed_y

        return score

    def check_ball_collision(self, other_ball):
        """處理兩顆球的圓形碰撞。"""
        if not self.is_moving or not other_ball.is_moving:
            return

        dx = other_ball.x - self.x
        dy = other_ball.y - self.y
        distance_sq = dx * dx + dy * dy
        minimum_distance = self.radius + other_ball.radius

        if distance_sq >= minimum_distance * minimum_distance:
            return
        if distance_sq == 0:
            dx = 1.0
            dy = 0
            distance_sq = 1.0

        distance = math.sqrt(distance_sq)
        nx = dx / distance
        ny = dy / distance

        overlap = minimum_distance - distance
        self.x -= nx * overlap * 0.5
        self.y -= ny * overlap * 0.5
        other_ball.x += nx * overlap * 0.5
        other_ball.y += ny * overlap * 0.5

        relative_x = other_ball.speed_x - self.speed_x
        relative_y = other_ball.speed_y - self.speed_y
        velocity_along_normal = relative_x * nx + relative_y * ny
        if velocity_along_normal >= 0:
            return

        impulse = -velocity_along_normal
        self.speed_x -= impulse * nx
        self.speed_y -= impulse * ny
        other_ball.speed_x += impulse * nx
        other_ball.speed_y += impulse * ny


######################定義函式區######################
def should_create_brick(level, col, row):
    """依關卡配置決定要建立哪個磚塊位置。"""
    if level == 1:
        return True
    if level == 2:
        return abs(col - 5) + abs(row - 4) <= 6
    if level == 3:
        return (
            row == 0
            or row == 8
            or col == 0
            or col == 10
            or (row + col) % 4 == 1
        )
    return True


def create_bricks(level=1):
    """建立磚塊清單，開始新遊戲時可以重新呼叫。"""
    new_bricks = []
    for col in range(bricks_col):
        for row in range(bricks_row):
            if not should_create_brick(level, col, row):
                continue
            x = col * (brick_w + brick_gap) + 70  # 從70開始排
            y = row * (brick_h + brick_gap) + 60  # 從60開始排
            color = (
                random.randint(30, 255),
                random.randint(30, 255),
                random.randint(30, 255),
            )
            brick = Brick(x, y, brick_w, brick_h, color)
            new_bricks.append(brick)
    special_bricks = random.sample(range(len(new_bricks)), 3)
    for special_brick in special_bricks:
        new_bricks[special_brick].is_special = True
    available_bricks = list(range(len(new_bricks)))
    for special_brick in special_bricks:
        available_bricks.remove(special_brick)
    reversal_bricks = random.sample(available_bricks, 4)
    for reversal_brick in reversal_bricks:
        new_bricks[reversal_brick].is_reversal = True
    return new_bricks


######################初始化設定######################
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()  # 啟動pygame


def create_tone(frequency, duration, volume=0.35, fade_end=True):
    """產生短音效，不需要額外的音效檔案。"""
    sample_rate = 44100
    sample_count = int(sample_rate * duration)
    samples = bytearray()
    for index in range(sample_count):
        envelope = 1.0 - (index / sample_count if fade_end else 0)
        sample = int(
            32767
            * volume
            * envelope
            * math.sin(2 * math.pi * frequency * index / sample_rate)
        )
        samples.extend(struct.pack("<h", sample))
    return pygame.mixer.Sound(buffer=bytes(samples))


sounds = {
    "brick": create_tone(180, 0.07, 0.24),
    "wall": create_tone(110, 0.035, 0.12),
    "pad": create_tone(260, 0.06, 0.18),
    "special": create_tone(520, 0.16, 0.38),
    "reversal": create_tone(330, 0.12, 0.28),
    "lost": create_tone(75, 0.25, 0.30),
    "win": create_tone(660, 0.35, 0.38),
}


def play_sound(name):
    if pygame.mixer.get_init() is not None:
        sounds[name].play()


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
TOTAL_LEVELS = 3
current_level = 1
bricks = create_bricks(current_level)

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
    4.5 * math.cos(math.radians(50)),
    -4.5 * math.sin(math.radians(50)),
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
level_transition_frames = 0
pending_level = 0
shake_frames = 0
shake_strength = 0
shake_x = 0
shake_y = 0
######################遊戲結束設定######################

######################主程式######################
while True:
    FPS.tick(60)  # 設定遊戲更新速度為60FPS
    world_surface = pygame.Surface(bg_size)
    world_surface.fill((0, 0, 0))

    if shake_frames > 0:
        shake_x = random.randint(-shake_strength, shake_strength)
        shake_y = random.randint(-shake_strength, shake_strength)
        shake_frames -= 1
    else:
        shake_x = 0
        shake_y = 0
    mos_x, mos_y = pygame.mouse.get_pos()  # 取得滑鼠座標
    pad.rect.x = mos_x - pad.rect.width // 2  # 底板中心跟隨滑鼠移動

    if pad.rect.x < 0:  # 限制底板不超出左邊界
        pad.rect.x = 0

    if pad.rect.x > bg_x - pad.rect.width:  # 限制底板不超出右邊界
        pad.rect.x = bg_x - pad.rect.width

    if not game_over:
        new_balls = []
        if level_transition_frames > 0:
            level_transition_frames -= 1
            if level_transition_frames == 0:
                current_level = pending_level
                pending_level = 0
                bricks = create_bricks(current_level)
                balls = [ball, ball2, ball3]
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
                if current_ball.is_lost:
                    continue
                if not current_ball.is_moving:
                    current_ball.x = (
                        pad.rect.x + pad.rect.width // 2 + current_ball.start_offset
                    )
                    current_ball.y = pad.rect.y - current_ball.radius
                else:
                    current_ball.move()
                    collision_score = current_ball.check_collision(bg_x, bg_y, pad, bricks)
                    score += collision_score
                    if collision_score > 0:
                        play_sound("brick")
                    elif current_ball.last_event in ("wall", "pad", "lost"):
                        play_sound(current_ball.last_event)
                    for brick in bricks:
                        if brick.reverse_balls:
                            brick.reverse_balls = False
                            play_sound("reversal")
                            shake_frames = 7
                            shake_strength = 3
                            for affected_ball in balls:
                                if affected_ball.is_moving and affected_ball.speed_y > 0:
                                    affected_ball.speed_y = -abs(affected_ball.speed_y)
                        if brick.spawn_balls:
                            brick.spawn_balls = False
                            play_sound("special")
                            shake_frames = 14
                            shake_strength = 6
                            spawn_speeds = [-2.5, 0.5, 2.5]
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
                                    -3.2,
                                )
                                new_ball.is_moving = True
                                new_balls.append(new_ball)

            balls.extend(new_balls)

            for first_index in range(len(balls)):
                for second_index in range(first_index + 1, len(balls)):
                    balls[first_index].check_ball_collision(balls[second_index])

        remaining_bricks = 0
        for brick in bricks:
            if not brick.hit:
                remaining_bricks += 1

        remaining_balls = 0
        for current_ball in balls:
            if not current_ball.is_lost:
                remaining_balls += 1

        if remaining_bricks == 0 and level_transition_frames == 0:
            if current_level < TOTAL_LEVELS:
                pending_level = current_level + 1
                level_transition_frames = 120
            else:
                game_over = True
                game_result = "你贏了！"
                play_sound("win")
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
                current_level = 1
                level_transition_frames = 0
                pending_level = 0
                bricks = create_bricks(current_level)
                balls = [ball, ball2, ball3]
                score = 0
                game_over = False
                game_result = ""
                shake_frames = 0
                shake_strength = 0
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
                if level_transition_frames == 0:
                    for current_ball in balls:
                        if not current_ball.is_lost:
                            current_ball.is_moving = True  # 開始移動球

    for brick in bricks:
        brick.draw(world_surface)

    pad.draw(world_surface)  # 繪製底板
    for current_ball in balls:
        if not current_ball.is_lost:
            current_ball.draw(world_surface)  # 繪製球

    score_text = font.render("分數：" + str(score), True, (255, 255, 255))
    world_surface.blit(score_text, (10, 10))
    high_score_text = font.render("最高分：" + str(high_score), True, (255, 255, 255))
    world_surface.blit(high_score_text, (bg_x - 180, 10))
    level_text = font.render(
        "關卡：" + str(current_level) + "/" + str(TOTAL_LEVELS),
        True,
        (255, 255, 255),
    )
    level_rect = level_text.get_rect(center=(bg_x // 2, 24))
    world_surface.blit(level_text, level_rect)

    if level_transition_frames > 0:
        transition_text = large_font.render(
            "進入關卡 " + str(pending_level),
            True,
            (255, 255, 255),
        )
        transition_rect = transition_text.get_rect(
            center=(bg_x // 2, bg_y // 2)
        )
        world_surface.blit(transition_text, transition_rect)

    if game_over:
        result_text = large_font.render(game_result, True, (255, 255, 255))
        result_rect = result_text.get_rect(center=(bg_x // 2, bg_y // 2 - 35))
        world_surface.blit(result_text, result_rect)
        final_score_text = font.render("最後分數：" + str(score), True, (255, 255, 255))
        final_score_rect = final_score_text.get_rect(center=(bg_x // 2, bg_y // 2 + 15))
        world_surface.blit(final_score_text, final_score_rect)
        restart_text = font.render("點擊滑鼠重新開始", True, (255, 255, 255))
        restart_rect = restart_text.get_rect(center=(bg_x // 2, bg_y // 2 + 60))
        world_surface.blit(restart_text, restart_rect)

    screen.fill((0, 0, 0))
    screen.blit(world_surface, (shake_x, shake_y))
    pygame.display.update()  # 更新視窗
