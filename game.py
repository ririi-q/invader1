import pygame
import sys
import random
import math

# Pygameの初期化
pygame.init()


# スクリーンのサイズ設定
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# ウィンドウのタイトル設定
pygame.display.set_caption('Stellalou vs Duffy Battle')

# 画像の読み込み
def load_image(filename, size):
    image = pygame.image.load(f"assets/images/{filename}").convert_alpha()
    return pygame.transform.scale(image, size)

# Bulletクラスの追加
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((4, 10))
        self.image.fill((255, 255, 255))  # 白い弾
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = -10  # 上方向に移動

    def update(self):
        self.rect.y += self.speed
        # 画面外に出たら削除
        if self.rect.bottom < 0:
            self.kill()

# EnemyBulletクラスを追加（Bulletクラスの後に追加）
class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((4, 10))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.speed_x = 0
        self.speed_y = 7
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.rect.x = self.x
        self.rect.y = self.y
        if (self.rect.top > SCREEN_HEIGHT or self.rect.bottom < 0 or 
            self.rect.left > SCREEN_WIDTH or self.rect.right < 0):
            self.kill()

# アイテムの基本クラス
class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, item_type):
        super().__init__()
        self.item_type = item_type
        # アイテムの種類に応じて画像を設定
        images = {
            'heal': 'heal_item.png',
            'speed': 'speed_item.png',
            'power': 'power_item.png',
            'defense': 'defense_item.png'
        }
        self.image = load_image(images[item_type], (30, 30))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 2

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# Playerクラスに射撃機能を追加
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # 通常の画像とヒット時の画像を保持
        self.normal_image = load_image("stellalou.png", (80, 100))
        self.hit_image = load_image("stellalou_hit.png", (80, 100))
        self.image = self.normal_image
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed = 5
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.max_hp = 100
        self.hp = self.max_hp
        # ヒットエフェクト用のタイマー
        self.hit_time = 0
        self.hit_duration = 100  # ミリ秒
        self.power_level = 0  # 弾の強化レベル
        self.defense_buff = 0  # 防御力強化
        
    def update(self):
        # キー入力を取得
        keys = pygame.key.get_pressed()
        
        # 左右移動
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed
            
        # スペースキーが押されている間、連続射撃
        if keys[pygame.K_SPACE]:
            self.shoot()
            
        # ヒットエフェクトの処理
        now = pygame.time.get_ticks()
        if now - self.hit_time < self.hit_duration:
            self.image = self.hit_image
        else:
            self.image = self.normal_image

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.power_level == 0:
                # 通常の弾
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
            elif self.power_level == 1:
                # 2列の弾
                for x in [self.rect.centerx - 20, self.rect.centerx + 20]:
                    bullet = Bullet(x, self.rect.top)
                    all_sprites.add(bullet)
                    bullets.add(bullet)
            else:
                # 3列の弾
                for x in [self.rect.centerx - 30, self.rect.centerx, self.rect.centerx + 30]:
                    bullet = Bullet(x, self.rect.top)
                    all_sprites.add(bullet)
                    bullets.add(bullet)

    def hit(self, damage):
        # ダメージ減少の処理を追加
        actual_damage = max(1, damage - self.defense_buff)
        self.hp -= actual_damage
        self.hit_time = pygame.time.get_ticks()
        
        # # ランダムにデバッフを適用
        # if random.random() < 0.5 and self.speed > 2:  # 50%の確率で速度低下
        #     self.speed = max(2, self.speed - 1)  # 最低速度は2
        # elif self.power_level > 0:  # 残りの50%で攻撃力低下
        #     self.power_level = max(0, self.power_level - 1)
        
        if self.hp <= 0:
            return True
        return False

    def apply_item(self, item_type):
        if item_type == 'heal':
            self.hp = min(self.hp + 30, self.max_hp)
        elif item_type == 'speed':
            self.speed += 1
        elif item_type == 'power':
            self.power_level = min(self.power_level + 1, 2)  # 最大レベル2
        elif item_type == 'defense':
            self.defense_buff += 1

# Enemyクラスの追加
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.hp = random.randint(1, 10)
        self.strength = random.randint(1, 5)
        size = int(40 * (1 + self.hp / 10))
        # 通常の画像とヒット時の画像を保持
        self.normal_image = load_image("duffy.png", (size, size))
        self.hit_image = load_image("duffy_hit.png", (size, size))
        self.image = self.normal_image
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speed = random.randrange(1, 3 + round_number)
        # ヒットエフェクト用のタイマー
        self.hit_time = 0
        self.hit_duration = 100
        # 射撃関連の変数を追加
        self.shoot_delay = random.randint(1000, 3000)  # 1-3秒のランダムな間隔
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speed = random.randrange(1, 5)
            
        # ヒットエフェクトの処理
        now = pygame.time.get_ticks()
        if now - self.hit_time < self.hit_duration:
            self.image = self.hit_image
        else:
            self.image = self.normal_image
            
        # 射撃処理
        if now - self.last_shot > self.shoot_delay:
            self.shoot()
            self.last_shot = now
            
    def shoot(self):
        bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
        all_sprites.add(bullet)
        enemy_bullets.add(bullet)

    def hit(self, damage=1):
        global score, enemies_defeated
        self.hp -= damage
        self.hit_time = pygame.time.get_ticks()
        if self.hp <= 0:
            score += self.strength * 10
            enemies_defeated += 1
            
            # アイテムドロップ
            if random.random() < 0.5:
                item_type = random.choice(['heal', 'speed', 'power', 'defense'])
                item = Item(self.rect.centerx, self.rect.centery, item_type)
                all_sprites.add(item)
                items.add(item)
                
            self.kill()

# Bossクラスの追加
class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.default_image = load_image("duffy_boss_default.png", (200, 240))
        self.damage_image = load_image("duffy_boss_damage.png", (200, 240))
        self.dead_image = load_image("duffy_boss_dead.png", (200, 240))
        self.image = self.default_image
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.top = 50
        
        self.max_hp = 10000 + 1000 * round_number
        self.hp = self.max_hp
        self.speed = 2 + round_number
        self.direction = 1  # 移動方向
        self.vertical_offset = 0  # 上下の揺れ
        self.phase = 0  # 攻撃パターン
        self.last_attack = pygame.time.get_ticks()
        self.attack_delay = 1000 / (5 / round_number)
        self.hit_time = 0
        self.hit_duration = 1000
        self.is_dead = False
        self.escape_speed = 5

    def update(self):
        now = pygame.time.get_ticks()
        
        if self.is_dead:
            self.image = self.dead_image
            self.rect.x += self.escape_speed
            self.rect.y -= self.escape_speed
            if self.rect.bottom < 0 or self.rect.left > SCREEN_WIDTH:
                self.kill()
            return

        # 通常の移動パターン
        if not self.is_dead:
            self.rect.x += self.speed * self.direction
            self.vertical_offset = math.sin(pygame.time.get_ticks() * 0.001) * 30
            self.rect.y = 50 + self.vertical_offset

            if self.rect.right > SCREEN_WIDTH - 50:
                self.direction = -1
            elif self.rect.left < 50:
                self.direction = 1

            # 攻撃パターン
            if now - self.last_attack > self.attack_delay:
                self.attack()
                self.last_attack = now

            # ダメージエフェクト
            if now - self.hit_time < self.hit_duration:
                self.image = self.damage_image
            else:
                self.image = self.default_image

    def attack(self):
        self.phase = (self.phase + 1) % 5
        if self.phase == 0:
            self._spread_attack()
        elif self.phase == 1:
            self._circle_attack()
        elif self.phase == 2:
            self._aimed_attack()
        elif self.phase == 3:
            self._laser_attack()
        else:
            self._random_attack()

    def _spread_attack(self):
        for angle in range(-60, 61, 30):
            bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
            bullet.speed_x = math.sin(math.radians(angle)) * 5
            bullet.speed_y = math.cos(math.radians(angle)) * 5
            all_sprites.add(bullet)
            enemy_bullets.add(bullet)

    def _circle_attack(self):
        for angle in range(0, 360, 45):
            bullet = EnemyBullet(self.rect.centerx, self.rect.centery)
            bullet.speed_x = math.sin(math.radians(angle)) * 4
            bullet.speed_y = math.cos(math.radians(angle)) * 4
            all_sprites.add(bullet)
            enemy_bullets.add(bullet)

    def _aimed_attack(self):
        if player:
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            angle = math.atan2(dy, dx)
            bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
            bullet.speed_x = math.cos(angle) * 6
            bullet.speed_y = math.sin(angle) * 6
            all_sprites.add(bullet)
            enemy_bullets.add(bullet)

    def _laser_attack(self):
        for x in range(3):
            bullet = EnemyBullet(self.rect.centerx + (x-1)*50, self.rect.bottom)
            all_sprites.add(bullet)
            enemy_bullets.add(bullet)

    def _random_attack(self):
        for _ in range(8):
            bullet = EnemyBullet(
                self.rect.centerx + random.randint(-100, 100),
                self.rect.bottom + random.randint(-50, 50)
            )
            all_sprites.add(bullet)
            enemy_bullets.add(bullet)

    def hit(self, damage):
        self.hp -= damage
        self.hit_time = pygame.time.get_ticks()
        if self.hp <= 0 and not self.is_dead:
            self.is_dead = True
            return True
        return False

# スプライトグループの作成
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
items = pygame.sprite.Group()
player = Player()
all_sprites.add(player)

# スプライトグループに敵用のグループを追加
enemies = pygame.sprite.Group()

# 敵の生成タイマー用の変数
enemy_spawn_delay = 2000  # 2秒
last_enemy_spawn = pygame.time.get_ticks()

# ゲームループ
clock = pygame.time.Clock()
running = True

# HPの表示をより見やすく
def draw_hp_bar(surface, x, y, hp, max_hp):
    BAR_LENGTH = 200
    BAR_HEIGHT = 20
    fill = (hp / max_hp) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surface, (0, 255, 0), fill_rect)
    pygame.draw.rect(surface, (255, 255, 255), outline_rect, 2)
    
    # HP数値の表示を追加
    font = pygame.font.Font(None, 24)
    hp_text = font.render(f'{hp}/{max_hp}', True, (255, 255, 255))
    text_rect = hp_text.get_rect(midleft=(x + BAR_LENGTH + 10, y + BAR_HEIGHT/2))
    surface.blit(hp_text, text_rect)

# グローバル変数の追加（game.pyの先頭付近に追加）
ROUND_TIME = 30000  # 30秒（ミリ秒）
COUNTDOWN_TIME = 10000  # 10秒（ミリ秒）
MAX_ENEMIES = 10
round_number = 1
score = 0
enemies_defeated = 0
round_start_time = 0
is_countdown = False
countdown_start = 0
is_boss_battle = False

# スコア表示用の関数
def draw_game_info(surface):
    font = pygame.font.Font(None, 36)
    # ラウンド情報
    round_text = font.render(f'Round: {round_number}', True, (255, 255, 255))
    surface.blit(round_text, (10, 40))
    
    # スコアと撃破数
    score_text = font.render(f'Score: {score}', True, (255, 255, 255))
    surface.blit(score_text, (10, 70))
    defeated_text = font.render(f'Defeated: {enemies_defeated}', True, (255, 255, 255))
    surface.blit(defeated_text, (10, 100))
    
    # 残り時間
    now = pygame.time.get_ticks()
    if not is_countdown:
        remaining = max(0, (ROUND_TIME - (now - round_start_time)) // 1000)
        time_text = font.render(f'Time: {remaining}s', True, (255, 255, 255))
    else:
        remaining = max(0, (COUNTDOWN_TIME - (now - countdown_start)) // 1000)
        time_text = font.render(f'Time: {remaining}s', True, (255, 255, 255))
        # カウントダウン中は画面中央にも大きく表示
        if remaining > 0:
            big_font = pygame.font.Font(None, 74)
            big_text = big_font.render(str(remaining), True, (255, 255, 0))
            text_rect = big_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
            surface.blit(big_text, text_rect)
    surface.blit(time_text, (SCREEN_WIDTH - 150, 10))

# ゲームループの開始前に追加
round_start_time = pygame.time.get_ticks()

# 敵の弾用のスプライトグループを追加
enemy_bullets = pygame.sprite.Group()

def draw_boss_hp(surface, boss):
    if boss and not boss.is_dead:
        BAR_LENGTH = 300
        BAR_HEIGHT = 20
        x = SCREEN_WIDTH - BAR_LENGTH - 10
        y = 10
        fill = (boss.hp / boss.max_hp) * BAR_LENGTH
        outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
        fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
        pygame.draw.rect(surface, (255, 0, 0), fill_rect)
        pygame.draw.rect(surface, (255, 255, 255), outline_rect, 2)
        
        font = pygame.font.Font(None, 24)
        hp_text = font.render(f'Boss HP: {boss.hp}/{boss.max_hp}', True, (255, 255, 255))
        text_rect = hp_text.get_rect(midright=(x - 10, y + BAR_HEIGHT/2))
        surface.blit(hp_text, text_rect)

while running:
    now = pygame.time.get_ticks()
    
    # ラウンド管理
    if not is_countdown:
        if now - round_start_time >= ROUND_TIME:
            is_countdown = True
            countdown_start = now
            # 敵を全て削除
            for enemy in enemies:
                enemy.kill()
            for bullet in enemy_bullets:
                bullet.kill()
    else:
        remaining = (COUNTDOWN_TIME - (now - countdown_start)) // 1000
        if remaining <= 0:
            is_countdown = False
            round_number += 1
            round_start_time = now
            
            # 3の倍数のラウンドでボス戦
            if round_number % 3 == 0:
                is_boss_battle = True
                boss = Boss()
                all_sprites.add(boss)
                enemies.add(boss)
    
    # 通常のゲームループ処理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # カウントダウン中は更新と敵の生成を停止
    if not is_countdown:
        all_sprites.update()
        
        # 弾と敵の衝突判定
        hits = pygame.sprite.groupcollide(bullets, enemies, True, False)
        for bullet, enemy_list in hits.items():
            for enemy in enemy_list:
                if isinstance(enemy, Boss):
                    enemy.hit(10)  # ボスへのダメージ
                else:
                    enemy.hit(1)  # 通常の敵へのダメージ

        # プレイヤーと敵の衝突判定
        hits = pygame.sprite.spritecollide(player, enemies, True)
        for enemy in hits:
            if player.hit(enemy.strength):
                # ゲームオーバー処理
                font = pygame.font.Font(None, 74)
                text = font.render('GAME OVER', True, (255, 0, 0))
                text_rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
                screen.blit(text, text_rect)
                pygame.display.flip()
                pygame.time.wait(2000)  # 2秒待機
                running = False
        
        # 敵の生成（ボス戦ではない場合）
        if now - last_enemy_spawn > enemy_spawn_delay and len(enemies) < MAX_ENEMIES and not is_boss_battle:
            enemy = Enemy()
            all_sprites.add(enemy)
            enemies.add(enemy)
            last_enemy_spawn = now
    
        # プレイヤーとアイテムの衝突判定
        hits = pygame.sprite.spritecollide(player, items, True)
        for item in hits:
            player.apply_item(item.item_type)
    
        # プレイヤーと敵の弾の衝突判定
        hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
        for bullet in hits:
            if player.hit(1):  # 弾は1ダメージ
                # ゲームオーバー処理
                font = pygame.font.Font(None, 74)
                text = font.render('GAME OVER', True, (255, 0, 0))
                text_rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
                screen.blit(text, text_rect)
                pygame.display.flip()
                pygame.time.wait(2000)
                running = False
    
    # 描画処理
    screen.fill((0, 0, 0))
    all_sprites.draw(screen)
    
    # HPの表示（スプライトの描画後に行う）
    draw_hp_bar(screen, 10, 10, player.hp, player.max_hp)
    # ボスのHPバーを表示（ボスが存在する場合）
    boss = next((sprite for sprite in enemies if isinstance(sprite, Boss)), None)
    if boss:
        draw_boss_hp(screen, boss)
        
    draw_game_info(screen)
    pygame.display.flip()
    
    # FPSを60に設定
    clock.tick(60)

# Pygameの終了
pygame.quit()
sys.exit() 