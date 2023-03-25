import pygame
import pygame_menu
import os
import time
import random

pygame.font.init()

WIDTH, HEIGHT = 900, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Grogu")
pygame.init()

# Load images
RED_ENEMY = pygame.image.load(os.path.join("assets", "red_enemy_r.png"))
RED_ENEMY = pygame.transform.scale(RED_ENEMY, (50, 50))
BLACK_ENEMY = pygame.image.load(os.path.join("assets", "black_enemy_r.png"))
BLACK_ENEMY = pygame.transform.scale(BLACK_ENEMY, (50, 50))
WHITE_ENEMY = pygame.image.load(os.path.join("assets", "white_enemy_r.png"))
WHITE_ENEMY = pygame.transform.scale(WHITE_ENEMY, (50, 50))

# Player player
BABY_YODA = pygame.image.load(os.path.join("assets", "baby_yoda.png"))
BABY_YODA = pygame.transform.scale(BABY_YODA, (100, 100))

# Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "red_laser_r.png"))
RED_LASER = pygame.transform.scale(RED_LASER, (100,30))
GREEN_LASER = pygame.image.load(os.path.join("assets", "green_laser_r.png"))
GREEN_LASER = pygame.transform.scale(GREEN_LASER, (100,30))
BLUE_LASER = pygame.image.load(os.path.join("assets", "blue_laser_r.png"))
BLUE_LASER = pygame.transform.scale(BLUE_LASER, (100,30))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "yellow_laser_r.png"))
YELLOW_LASER = pygame.transform.scale(YELLOW_LASER, (100,30))

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "space.jpg")), (WIDTH, HEIGHT))
menu_theme = pygame_menu.themes.THEME_DARK
menu_width = 500
menu_height = 500
# my_theme = pygame_menu.themes.Theme(background_color=(255, 255, 255, 255))
menu = pygame_menu.Menu("Choose one", menu_width, menu_height, theme=menu_theme)
# Health
HEALTH = pygame.image.load(os.path.join("assets", "6-pixel-heart-1.png"))
HEALTH = pygame.transform.scale(HEALTH, (70, 70))

HIGH_SCORE = 0

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Health:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.img = HEALTH
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)

class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.color = None
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = BABY_YODA
        self.laser_img = YELLOW_LASER
        self.laser = 0
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        if self.laser == 1:
                            if obj.color == "red":
                                obj.health -= 150
                            elif obj.color == "black":
                                obj.health -= 100
                            else:
                                obj.health -= 50
                        elif self.laser == 2:
                            if obj.color == "red":
                                obj.health -= 100
                            elif obj.color == "black":
                                obj.health -= 200
                            else:
                                obj.health -= 50
                        elif self.laser == 3:
                            obj.health -= 100
                        if obj.health <= 0:
                            objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window, health):
        super().draw(window)
        self.health = health
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0),
                         (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (
        self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health / self.max_health),
        10))

    def change_laser_color(self, laser_img_color):
        if laser_img_color == "Red":
            self.laser_img = RED_LASER
            self.laser = 1
        elif laser_img_color == "Black":
            self.laser_img = GREEN_LASER
            self.laser = 2
        elif laser_img_color == "White":
            self.laser_img = BLUE_LASER
            self.laser = 3


class Enemy(Ship):
    COLOR_MAP = {
        "red": (RED_ENEMY, RED_LASER),
        "black": (BLACK_ENEMY, GREEN_LASER),
        "white": (WHITE_ENEMY, BLUE_LASER)
    }

    def __init__(self, x, y, color, health=100):
        if color == "red":
            health = 300
        elif color == "black":
            health = 200
        elif color == "white":
            health = 100
        super().__init__(x, y, health)
        self.color = color
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x - 20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

level = 0
lives = 5
enemies = []
healths = []
wave_length = 5
enemy_vel = 1

player_vel = 5
laser_vel = 5
health_vel = 0
health_wave_length = 1 #
player = Player(300, 630)
health_wave_length = 0

lost = False
lost_count = 0
def main():
    run = True
    FPS = 90
    global init
    global level
    global lives
    global enemies
    global healths
    global wave_length
    global health_wave_length #
    global enemy_vel
    global health_wave_length
    global health_vel
    global lost
    global lost_count
    global player_vel
    global laser_vel
    global player
    global HIGH_SCORE
    if not init:
        level = 0
        lives = 5


        enemies = []
        wave_length = 5
        enemy_vel = 1

        healths = []
        health_wave_length = 1
        health_vel = 1

        player_vel = 5
        laser_vel = 5

        lost = False
        lost_count = 0
        init = True

    main_font = pygame.font.SysFont("arial", 40)
    lost_font = pygame.font.SysFont("arial", 40)
    clock = pygame.time.Clock()
    player.change_laser_color(weapon)

    def choose_new_weapon():
        menu.enable()
        menu.mainloop(WIN)

    def redraw_window():
        WIN.blit(BG, (0, 0))
        # draw text
        lives_label = main_font.render(f"Enemies to miss: {lives}", 1, (255, 255, 255))
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))
        high_score_label = main_font.render(f"High score: {HIGH_SCORE}", 1, (255, 255, 255))

        WIN.blit(high_score_label, (WIDTH / 2.5 , 10))
        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        for health in healths:
            health.draw(WIN)

        player.draw(WIN, player.health)

        if lost:
            lost_label = lost_font.render("You Lost!!", 1, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH / 2 - lost_label.get_width() / 2, 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
                if level > HIGH_SCORE:
                    HIGH_SCORE = level
                player.health = 100
                init = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 2
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100),
                              random.choice(["red", "black", "white"]))
                enemies.append(enemy)
            # Health
            for j in range(health_wave_length):
                health = Health(random.randrange(50, WIDTH-100), random.randrange(-1500, -100))
                healths.append(health)
            if level != 1:
                choose_new_weapon()


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and player.x - player_vel > 0:  # left
            player.x -= player_vel
        if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and player.x + player_vel + player.get_width() < WIDTH:  # right
            player.x += player_vel
        if (keys[pygame.K_w] or keys[pygame.K_UP]) and player.y - player_vel > 0:  # up
            player.y -= player_vel
        if (keys[pygame.K_s] or keys[
            pygame.K_DOWN]) and player.y + player_vel + player.get_height() + 15 < HEIGHT:  # down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2 * 60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        for health in healths[:]:
            health.move(health_vel)
            # enemy.move_lasers(laser_vel, player)

            # if random.randrange(0, 2*60) == 1:
            #     enemy.shoot()

            if collide(health, player):
                # player.health += 30
                if player.health + 30 > 100:
                    player.health = 100
                elif player.health + 30 <= 100:
                    player.health += 30
                if lives < 5:
                    lives += 1
                healths.remove(health)
            # elif enemy.y + enemy.get_height() > HEIGHT:
            #     lives -= 1
            #     enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)


weapon = "red"
init = False

def select_weapon(weapons, selected_weapon):
    global weapon
    weapon = selected_weapon
    main()


def main_menu():
    title_font = pygame.font.SysFont("arial", 40)

    run = True
    weapons = {
        'Red': {
            'damage-red': 200,
            'damage-black': 100,
            'damage-white': 50
        },
        'Black': {
            'damage-red': 100,
            'damage-black': 200,
            'damage-white': 50
        },
        'White': {
            'damage-red': 50,
            'damage-black': 100,
            'damage-white': 200
        }
    }


    menu.disable()
    for weapon_name in weapons.keys():
        img_name = str(weapon_name).lower() + '_gun.png'
        PATH = os.path.join("assets", img_name)
        menu.add.image(PATH, angle=0, scale=(0.35, 0.35), scale_smooth=True)
        menu.add.button(weapon_name, select_weapon, weapons, weapon_name)

    while run:
        WIN.blit(BG, (0, 0))
        title_label = title_font.render("Press the mouse to begin...", 1, (255, 255, 255))
        WIN.blit(title_label, (WIDTH / 2 - title_label.get_width() / 2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                menu.enable()
                menu.mainloop(WIN)
    pygame.display.update()
    pygame.quit()


main_menu()
