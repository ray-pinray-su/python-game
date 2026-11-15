######################載入套件######################
import pygame
import sys
import random
import os

os.chdir(sys.path[0])  # 將工作目錄切換到程式所在的資料夾

######################全域變數######################
score = 0
highest_score = 0
game_over = False
initial_player_y = 0
spring_chance = 0.2
springs = []


######################物件類別######################
class Player:
    def __init__(self, x, y, width, height, color):
        """
        初始化主角/Initialize the player\n
        x,y: 主角的左上角座標/Top-left position\n
        width,height: 主角的寬度與高度/Player's width and height\n
        color: 主角的顏色(RGB格式)/Player's color(RGB)\n
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.speed = 5
        self.velocity_y = 0
        self.jump_power = -12
        self.gravity = 0.5
        self.on_plaform = False

    def draw(self, display_area):
        """
        繪製主角/Draw the player\n
        display_area: 繪製主角的目標視窗\n
        """
        pygame.draw.rect(display_area, self.color, self.rect)

    def move(self, direction, bg_x):
        """
        移動主角並處理穿牆效果/Move the wrap the player\n
        direction: 移動方向(1:向右/Right, -1:向左/Left)/Direction(1: right, -1: left)\n
        bg_x: 遊戲視窗的寬度, 用於判斷是否穿牆/Window width for wrapping\n
        """
        self.rect.x += direction * self.speed
        if self.rect.right < 0:
            self.rect.left = bg_x
        elif self.rect.left > bg_x:
            self.rect.right = 0

    def apply_gravity(self):
        """
        應用重力效果/Apply gravity\n
        更新垂直速度與位置/Update vertical velocity and position\n
        """
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

    def check_platform_collision(self, platforms):
        """
        檢查主角是否與平台碰撞/Check platform collision\n
        platform: 要檢查與平台的碰撞/Platform to check\n
        """
        if self.velocity_y > 0:
            check_points = max(1, int(abs(self.velocity_y) / 5))
            step_y = self.velocity_y / check_points
            for platform in platforms:
                for i in range(check_points):
                    test_rect = self.rect.copy()
                    test_rect.y += i * step_y
                    if (
                        test_rect.bottom >= platform.rect.top
                        and test_rect.bottom <= platform.rect.bottom
                        and test_rect.right >= platform.rect.left
                        and test_rect.left <= platform.rect.right
                    ):
                        self.rect.bottom = platform.rect.top
                        self.velocity_y = self.jump_power
                        self.on_plaform = True
                        return True
        return False


class Platform:
    def __init__(self, x, y, width, height, color):
        """
        初始化平台/Initialize the platform\n
        x,y: 平台的左上角座標/Top-left position/n
        width,height: 平台的寬度與高度/Platform's width and height\n
        color: 平台的顏色(RGB格式)/Platform's color(RGB)\n
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color

    def draw(self, display_area):
        """
        繪製平台/Draw the platform\n
        display_area: 繪製平台的目標視窗/Target drawing surface\n
        """
        pygame.draw.rect(display_area, self.color, self.rect)


class Spring:
    def __init__(self, x, y, width, height, color):
        """
        初始化彈簧道具/Ceate a spring\n
        x,y: 彈簧的左上角座標/Top-left corner\n
        width,height: 彈簧的寬度與高度/Spring size\n
        color: 彈簧的顏色(RGB格式)/Spring color(RGB)\n
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color

    def draw(self, display_area):
        """
        繪製彈簧/Draw the spring\n
        display_area: 繪製彈簧的目標視窗/window to draw on\n
        """
        pygame.draw.rect(display_area, self.color, self.rect)

    def move_with_platform(self, dy):
        """
        隨平台移動/Move with the platform\n
        dy: 垂直移動的距離/Vertical distance\n
        """
        self.rect.y += dy


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

#####################平台設定######################
platform_w = 60
platform_h = 10
platforms = []
platform_x = (bg_x - platform_w) // 2
platform_y = bg_y - platform_h - 10
platform = Platform(platform_x, platform_y, platform_w, platform_h, (255, 255, 255))
platforms.append(platform)

platform_count = random.randint(8, 10) + 10
for i in range(platform_count):
    x = random.randint(0, bg_x - platform_w)
    y = (bg_y - 100) - (i * 60)
    platform = Platform(x, y, platform_w, platform_h, (255, 255, 255))
    platforms.append(platform)

######################字型設定######################
font = pygame.font.Font("../fonts/NotoSansTC-Regular (1).ttf", 24)


######################自訂函式######################
def update_camera():
    """
    更新相機位置和平台/Update the camera and platforms\n
    -當玩家上升到螢幕的一半高度以上時,固定玩家在螢幕中間/Above half height, keep the player in the middle\n
    -將所有平台向下移動,製造出玩家上升的效果/Move all platforms down so the player seems to climb\n
    -移除超出螢幕的舊平台/Remove platforms below the screen\n
    -生成新的平台/Add new platforms above\n
    -更新所有彈簧位置,並移除超出畫面的彈簧/Move springs and remove those off-screen\n
    """
    global score, initial_player_y, springs
    screen_middle = bg_y // 2

    if player.rect.y < screen_middle:
        camera_move = screen_middle - player.rect.y
        player.rect.y = screen_middle

        score += int(camera_move / 10)

        for platform in platforms:
            platform.rect.y += camera_move

        for spring in springs:
            spring.move_with_platform(camera_move)

        y_min = bg_y
        for platform in platforms[:]:
            if platform.rect.top > bg_y:
                platforms.remove(platform)
            if platform.rect.top < y_min:
                y_min = platform.rect.top

        for spring in springs[:]:
            if spring.rect.top > bg_y:
                springs.remove(spring)

        if len(platforms) < platform_count:
            x = random.randint(0, bg_x - platform_w)
            y = y_min - 60
            platform = Platform(x, y, platform_w, platform_h, (255, 255, 255))
            platforms.append(platform)

            if random.random() < spring_chance:
                spring_w = 20
                spring_h = 10
                spring_x = platform.rect.x + (platform_w - spring_w) // 2
                spring_y = platform.rect.y - spring_h
                spring = Spring(spring_x, spring_y, spring_w, spring_h, (255, 215, 0))
                springs.append(spring)


def reset_game():
    """
    重置遊戲狀態/Reset the game state\n
    -重設玩家位置/Reset player position\n
    -清空並重新生成平台/Clear and rebuild platforms\n
    -清空並重置彈簧/Clear and reset springs\n
    -重設分數和遊戲狀態/Reset the score and game state\n
    """
    global score, game_over, platforms, initial_player_y, highest_score
    player.rect.x = (bg_x - player_w) // 2
    player.rect.y = bg_y - player_h - 50
    player.velocity_y = 0

    platforms.clear()
    springs.clear()

    platform_x = (bg_x - platform_w) // 2
    platform_y = bg_y - platform_h - 10
    platform = Platform(platform_x, platform_y, platform_w, platform_h, (255, 255, 255))
    platforms.append(platform)

    for i in range(platform_count - 1):
        x = random.randint(0, bg_x - platform_w)
        y = (bg_y - 100) - (i * 60)
        platform = Platform(x, y, platform_w, platform_h, (255, 255, 255))
        platforms.append(platform)

        if random.random() < spring_chance:
            spring_w = 20
            spring_h = 10
            spring_x = platform.rect.x + (platform_w - spring_w) // 2
            spring_y = platform.rect.y - spring_h
            spring = Spring(spring_x, spring_y, spring_w, spring_h, (255, 215, 0))
            springs.append(spring)

    score = 0
    game_over = False
    initial_player_y = player.rect.y


######################主程式######################
while True:
    FPS.tick(60)
    screen.fill((0, 0, 0))

    if not game_over:
        update_camera()

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            player.move(-1, bg_x)
        if keys[pygame.K_RIGHT]:
            player.move(1, bg_x)

        player.apply_gravity()
        player.check_platform_collision(platforms)

        if player.rect.top > bg_y:
            game_over = True
            if score > highest_score:
                highest_score = score
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN and game_over:
            reset_game()
    for platform in platforms:
        platform.draw(screen)

    for spring in springs:
        spring.draw(screen)
    player.draw(screen)
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    if game_over:
        game_over_text = font.render(
            "Game Over! Press any key to restart.", True, (255, 255, 255)
        )
        highest_score_text = font.render(
            f"Highest Score: {highest_score}", True, (255, 255, 255)
        )
        text_rect = game_over_text.get_rect(center=(bg_x / 2, bg_y / 2))
        score_rect = highest_score_text.get_rect(center=(bg_x / 2, bg_y / 2 + 40))
        screen.blit(game_over_text, text_rect)
        screen.blit(highest_score_text, score_rect)
    pygame.display.update()
