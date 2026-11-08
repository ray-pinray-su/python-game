######################載入套件######################
import pygame
import sys
import random


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


######################自訂函式######################
def update_camera():
    """
    更新相機位置和平台/Update the camera and platforms\n
    -當玩家上升到螢幕的一半高度以上時,固定玩家在螢幕中間/Above half height, keep the player in the middle\n
    -將所有平台向下移動,製造出玩家上升的效果/Move all platforms down so the player seems to climb\n
    -移除超出螢幕的舊平台/Remove platforms below the screen\n
    -生成新的平台/Add new platforms above\n
    """
    screen_middle = bg_y // 2

    if player.rect.y < screen_middle:
        camera_move = screen_middle - player.rect.y
        player.rect.y = screen_middle

        for platform in platforms:
            platform.rect.y += camera_move

        y_min = bg_y
        for platform in platforms:
            if platform.rect.top > bg_y:
                platforms.remove(platform)
            if platform.rect.top < y_min:
                y_min = platform.rect.top

        if len(platforms) < platform_count:
            x = random.randint(0, bg_x - platform_w)
            y = y_min - 60
            platform = Platform(x, y, platform_w, platform_h, (255, 255, 255))
            platforms.append(platform)


######################主程式######################
while True:
    FPS.tick(60)
    screen.fill((0, 0, 0))

    update_camera()

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        player.move(-1, bg_x)
    if keys[pygame.K_RIGHT]:
        player.move(1, bg_x)

    player.apply_gravity()
    player.check_platform_collision(platforms)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    for platform in platforms:
        platform.draw(screen)

    player.draw(screen)
    pygame.display.update()
