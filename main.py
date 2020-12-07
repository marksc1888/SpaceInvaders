import pygame
import os
import time
import random
pygame.font.init()

W_WIDTH, W_HEIGHT = 750, 1000
WINDOW = pygame.display.set_mode((W_WIDTH, W_HEIGHT))
pygame.display.set_caption("Project-SC")

#dimensions for the scaled sprites
PLAYER_WIDTH, PLAYER_HEIGHT= 90, 99 #original dimensions -> W: 30, H: 33
MSHIP_WIDTH, MSHIP_HEIGHT = 168,  260 #original dimensions -> W: 42, H: 65
SINGLE_WIDTH, SINGLE_HEIGHT = 90, 87 #original dimensions -> W: 30, H: 29
DOUBLE_WIDTH, DOUBLE_HEIGHT = 86, 87 #original dimensions -> W: 28, H: 29
PLASERDEFAULT_WIDTH, PLASERDEFAULT_HEIGHT = 12, 18 #original dimensions -> W: 4, H: 6
ELASERDEFAULT_WIDTH, ELASERDEFAULT_HEIGHT = 12, 12 #original dimensions -> W: 4, H: 4
ELASERSTRONG_WIDTH, ELASERSTRONG_HEIGHT = 12, 36 #original dimensions -> W: 4, H: 12

#loading in the assets
BACKGROUND = pygame.transform.scale(pygame.image.load(os.path.join("assets","SPACE_BACKGROUND.png")), (1200, 1000) )
PLAYER = pygame.transform.scale(pygame.image.load(os.path.join("assets","Player-Model.png")), (PLAYER_WIDTH, PLAYER_HEIGHT))
MOTHERSHIP = pygame.transform.scale(pygame.image.load(os.path.join("assets", "Enemy-Mothership-Model.png")), (MSHIP_WIDTH, MSHIP_HEIGHT))
SINGLESHOT = pygame.transform.scale(pygame.image.load(os.path.join("assets", "Enemy-Single_Shot-Model.png")), (SINGLE_WIDTH, SINGLE_HEIGHT))
DOUBLESHOT = pygame.transform.scale(pygame.image.load(os.path.join("assets", "Enemy-Double_Shot-Model.png")), (DOUBLE_WIDTH, DOUBLE_HEIGHT))
PLASERDEFAULT = pygame.transform.scale(pygame.image.load(os.path.join("assets", "Player-Laser-Default.png")), (PLASERDEFAULT_WIDTH, PLASERDEFAULT_HEIGHT))
ELASERDEFAULT = pygame.transform.scale(pygame.image.load(os.path.join("assets", "Enemy-Laser-Default.png")), (ELASERDEFAULT_WIDTH, ELASERDEFAULT_HEIGHT))
ELASERSTRONG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "Enemy-Laser-Strong.png")), (ELASERSTRONG_WIDTH, ELASERSTRONG_HEIGHT))

class Laser:
    def __init__(self, x, y, v, sprite):
        self.x = x
        self.y = y
        self.v = v
        self.sprite = sprite
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self):
        WINDOW.blit(self.sprite, (self.x, self.y))

    def move(self, v):
        self.y += v

    def off_screen(self):
        return not(self.y <= W_HEIGHT and self.y >= 0)

    def collision(self, object):
        return collide(self, object)

class Ship:
    COOLDOWN = 30
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.v = 5
        self.lv = 5
        self.hp = 100
        self.sprite = None
        self.laserSprite = None
        self.lasers = []
        self.cooldownCount = 0

    def draw(self):
        WINDOW.blit(self.sprite, (self.x, self.y))
        for laser in self.lasers:
            laser.draw()

    def move_lasers(self, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(self.lv)
            if laser.off_screen():
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.hp -= 10
                self.lasers.remove(laser)


    def cooldown(self):
        if self.cooldownCount >= self.COOLDOWN:
            self.cooldownCount = 0
        elif self.cooldownCount > 0:
            self.cooldownCount += 1

    def shoot(self):
        if self.cooldownCount == 0:
            laser = Laser(self.x + self.getWidth() / 2 - PLASERDEFAULT_WIDTH / 2, self.y, self.lv, self.laserSprite)
            self.lasers.append(laser)
            self.cooldownCount = 1

    def getWidth(self):
        return self.sprite.get_width()
    def getHeight(self):
        return self.sprite.get_height()

class Player(Ship):
    width = PLAYER_WIDTH
    height = PLAYER_HEIGHT

    def __init__(self):
        super().__init__(375 - (self.width / 2), 850)
        self.sprite = PLAYER
        self.laserSprite = PLASERDEFAULT
        self.mask = pygame.mask.from_surface(self.sprite)
        self.maxHealth = 100
        self.lv = (self.v + 1) * -1

    def move_lasers(self, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(self.lv)
            if laser.off_screen():
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.lasers.remove(laser)

class Enemy(Ship):
    SHIP_TYPES = {
        "single": (SINGLESHOT, ELASERSTRONG, 10, 8), #last two are damage & probability constant
        "double": (DOUBLESHOT, ELASERDEFAULT, 5, 2)
    }

    def __init__(self, x, y, type):
        super().__init__(x, y)
        self.sprite, self.laserSprite, self.damage, self.prob = self.SHIP_TYPES[type]
        self.mask = pygame.mask.from_surface(self.sprite)
        self.v = 1
        self.lv = self.v + 1

    def move(self):
        self.y += self.v

    def move_lasers(self, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(self.lv)
            if laser.off_screen():
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.hp -= self.damage
                self.lasers.remove(laser)

    def shoot(self):
        if self.cooldownCount == 0:
            laser = Laser(self.x + self.getWidth() / 2 - PLASERDEFAULT_WIDTH / 2, self.y + self.getHeight(), self.lv, self.laserSprite)
            self.lasers.append(laser)
            self.cooldownCount = 1

def collide(object1, object2):
    offset_x = object2.x - object1.x
    offset_y = object2.y - object1.y
    return object1.mask.overlap(object2.mask, (int(offset_x), int(offset_y))) != None

#MAIN METHOD
def main():
    run = True
    FPS = 60

    wave = 0
    lives = 5

    main_font = pygame.font.SysFont("consolas", 30)
    lost_font = pygame.font.SysFont("consolas", 60)

    enemies = []
    enemy_count = 5

    clock = pygame.time.Clock()

    player = Player()

    hasLost = False
    lostCount = 0

    def redraw_window():
        WINDOW.blit(BACKGROUND, (0, 0))
        level_label = main_font.render(f"Wave: {wave}", 1, (255, 255, 255))
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
        if player.hp <= 0:
            hp_label = main_font.render(f"HP: 0", 1, (255, 255, 255))
        else:
            hp_label = main_font.render(f"HP: {player.hp}", 1, (255, 255, 255))
        WINDOW.blit(level_label, (10, 10))
        WINDOW.blit(hp_label, (300, 10))

        for enemy in enemies:
            enemy.draw()
        player.draw()

        if hasLost:
            lost_label = lost_font.render("YOU HAVE LOST.", 1, (255, 0, 0))
            WINDOW.blit(lost_label, (W_WIDTH / 2 - lost_label.get_width() / 2, W_HEIGHT / 2 - lost_label.get_height() / 2) )

        pygame.display.update()


    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.hp <= 0:
            hasLost = True
            lostCount += 1

        if hasLost:
            if lostCount > FPS * 5:
                run = False
            else:
                continue

        if len(enemies) == 0:
            wave += 1
            enemy_count += 5
            for i in range(enemy_count):
                enemy = Enemy(random.randrange(50, W_WIDTH - 100), random.randrange(-1500, -100), random.choice(["single", "double"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x > 0:
            player.x -= player.v
        if keys[pygame.K_d] and player.x < W_WIDTH - player.getWidth():
            player.x += player.v
        if keys[pygame.K_w] and player.y > 0:
            player.y -= player.v
        if keys[pygame.K_s] and player.y < W_HEIGHT - player.getHeight() - 1:
            player.y += player.v
        if keys[pygame.K_SPACE]:
            player.shoot()
        for enemy in enemies[:]:
            enemy.move()
            enemy.move_lasers(player)
            if random.randrange(0, FPS * enemy.prob) == 1:
                enemy.shoot()
            if collide(enemy, player):
                player.hp -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.getHeight() > W_HEIGHT:
                lives -= 1
                enemies.remove(enemy)


        player.move_lasers(enemies)

def main_menu():
    titlefont = pygame.font.SysFont("consolas", 50)
    run = True
    while run:
        WINDOW.blit(BACKGROUND, (0,0))
        title_label = titlefont.render("Press the mouse to begin.", 1, (255, 255, 255))
        WINDOW.blit(title_label, (W_WIDTH / 2 - title_label.get_width() / 2, W_HEIGHT / 2 - title_label.get_height() / 2))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()

main_menu()
#SingleShot: faster, shoots one bullet
#Doubleshot: normal speed, shoots 2 bullets
#HeavyShot: slow, shoots one high-damage shot