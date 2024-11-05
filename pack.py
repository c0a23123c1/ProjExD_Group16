import pygame
import sys
import random
import math

# 初期設定
pygame.init()
screen_width, screen_height = 960,360
cell_size = 40
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Pac-Man Like Maze Game")

# 色の設定
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)  # 回復表示用の色

# キャラクター設定
pacman_size = cell_size - 4
ghost_size = cell_size - 4
dot_size = 5
normal_speed = 5
boosted_speed = 8  # 加速時の速度
pacman_speed = normal_speed
ghost_speed = 2


# 体力設定
max_health = 100
current_health = max_health
healing_amount = 20  # 回復量

# 敵の数の設定
initial_ghost_count = 5  # 初期の敵の数

# 敵停止スキルのタイマー設定
ghost_freeze_duration = 2000  # 停止時間 (ミリ秒単位)
ghost_freeze_timer = 0  # タイマーの初期値


# 迷路の定義 (1が壁, 0が道)
maze = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1],
    [1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

# プレイヤーの初期位置
pacman_x, pacman_y = 1 * cell_size, 1 * cell_size

# 壁のリスト作成
walls = []
for row_index, row in enumerate(maze):
    for col_index, cell in enumerate(row):
        if cell == 1:
            walls.append(pygame.Rect(col_index * cell_size, row_index * cell_size, cell_size, cell_size))

# ゴーストの位置をランダムに初期化
ghosts = [{"x": 5 * cell_size, "y": 5 * cell_size} for _ in range(3)]

class WallHack:
    def __init__(self):
        self.enabled = False
    
    def toggle(self):
        self.enabled = not self.enabled
wallhack = WallHack()
# プレイヤーの移動（壁との衝突を考慮）
def move_pacman(keys):
    global pacman_x, pacman_y,pacman_speed

    # Shiftキーが押されている間は加速
    if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
        pacman_speed = boosted_speed
    else:
        pacman_speed = normal_speed


    new_x, new_y = pacman_x, pacman_y
    if keys[pygame.K_LEFT]:
        new_x -= pacman_speed
    if keys[pygame.K_RIGHT]:
        new_x += pacman_speed
    if keys[pygame.K_UP]:
        new_y -= pacman_speed
    if keys[pygame.K_DOWN]:
        new_y += pacman_speed

    # 壁との衝突判定
    pacman_rect = pygame.Rect(new_x, new_y, pacman_size, pacman_size)
    if wallhack.enabled or not any(pacman_rect.colliderect(wall) for wall in walls):
        pacman_x, pacman_y = new_x, new_y  # 壁に衝突しない場合のみ位置を更新

# ゴーストの移動
def move_ghosts():
    for ghost in ghosts:
        dx, dy = pacman_x - ghost["x"], pacman_y - ghost["y"]
        dist = math.hypot(dx, dy)
        if dist != 0:
            dx, dy = dx / dist, dy / dist
            new_x = ghost["x"] + dx * ghost_speed
            new_y = ghost["y"] + dy * ghost_speed
            ghost_rect = pygame.Rect(new_x, new_y, ghost_size, ghost_size)
            if not any(ghost_rect.colliderect(wall) for wall in walls):
                ghost["x"], ghost["y"] = new_x, new_y  # 壁に衝突しない場合のみ位置を更新


# 回復スキル
def heal():
    global current_health
    if current_health < max_health:
        current_health = min(current_health + healing_amount, max_health)  # 最大HPを超えないようにする

# 敵をランダムに消去する関数
def eliminate_random_enemy():
    if ghosts:
        ghosts.pop(random.randint(0, len(ghosts) - 1))

# 敵を2秒間停止させるスキル
def freeze_ghosts():
    global ghost_freeze_timer
    ghost_freeze_timer = ghost_freeze_duration  # 2秒間のタイマーをセット


# 描画処理
def draw_game():
    screen.fill(BLACK)
    
    # 壁の描画
    for wall in walls:
        pygame.draw.rect(screen, BLUE, wall)
    
    # プレイヤーの描画
    pygame.draw.rect(screen, YELLOW, pygame.Rect(pacman_x, pacman_y, pacman_size, pacman_size))
    
    # ゴーストの描画
    for ghost in ghosts:
        pygame.draw.rect(screen, RED, pygame.Rect(ghost["x"], ghost["y"], ghost_size, ghost_size))
    
    # HPバーの描画
    pygame.draw.rect(screen, RED, (10, 10, max_health, 10))  # 最大体力
    pygame.draw.rect(screen, GREEN, (10, 10, current_health, 10))  # 現在の体力

# ゲームループ
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_w:
            wallhack.toggle()
    
    # キー入力の取得
    keys = pygame.key.get_pressed()

    # ランダムに敵を消去
    if keys[pygame.K_e]:
        eliminate_random_enemy()
    
    # 回復スキル発動
    if keys[pygame.K_f]:
        heal()


    # 敵を2秒停止するスキル発動
    if keys[pygame.K_s]:
        freeze_ghosts()
    
    # 各関数の実行
    move_pacman(keys)

    # ゴーストの停止タイマーを更新
    if ghost_freeze_timer > 0:
       ghost_freeze_timer -= clock.get_time()  # タイマーを減少
    else:
        move_ghosts()

    draw_game()
    pygame.display.flip()
    clock.tick(30)
