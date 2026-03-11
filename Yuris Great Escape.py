import datetime
import random
import threading
import time
from math import degrees
from threading import Thread
from xmlrpc.client import DateTime
import pygame
import winsound
from pygame.examples.music_drop_fade import volume
import lib.textoutline as textoutline
import math
import os
import ctypes
import sys
ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
pygame.init()
pygame.display.set_caption("Yuri's Great Escape")
windowSize = (1000,800)
blockSize = 50
levelId = 1
won = False
# startTime = time.time()
winTime = 0
window = pygame.display.set_mode(windowSize)
import lib.ragelevel as level
character = pygame.transform.scale(pygame.image.load("assets/player.png").convert_alpha(),(50,50))
gun = pygame.transform.scale(pygame.image.load("assets/gun.png").convert_alpha(),(50,50))
crown = pygame.image.load("assets/crown.png").convert_alpha()
crown2 = pygame.image.load("assets/crown2.png").convert_alpha()
loosercrown = pygame.image.load("assets/loosercrown.png").convert_alpha()
backgroundico = pygame.image.load("assets/bac.png").convert_alpha()
chibi_monika = pygame.image.load("assets/Chibi_Monika.png").convert_alpha()
chibi_monika = pygame.transform.scale(chibi_monika, (150, 194))  # Resize if needed
chibi_yuri = pygame.image.load("assets/chibi_yuri.png").convert_alpha()


bulletico = pygame.transform.scale(pygame.image.load("assets/Game Asset.png").convert_alpha(),(50,50))
bulletico2 = pygame.transform.scale(pygame.image.load("assets/bullet2.png").convert_alpha(),(50,50))
bulletico3 = pygame.transform.flip(pygame.transform.scale(pygame.image.load("assets/bullet2.png").convert_alpha(),(50,50)),True,False)


clockico = pygame.transform.scale(pygame.image.load("assets/clock.png").convert_alpha(),(50,50))
leaficos = [
pygame.transform.scale(pygame.image.load("assets/Cherry.png").convert_alpha(),(51,33)),
pygame.transform.scale(pygame.image.load("assets/leaf2.png").convert_alpha(),(51,33)),
pygame.transform.scale(pygame.image.load("assets/Cherry3.png").convert_alpha(),(51,33))
]
pygame.display.set_icon(character)
levelPause = 0

class Vec2d:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def length(self):
        return abs(self.x) + abs(self.y)

    def distance(self, other):
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def add(self, other):
        self.x += other.x
        self.y += other.y

    def subtract(self, other):
        self.x -= other.x
        self.y -= other.y

    def withX(self, x):
        self.x = x

    def withY(self, y):
        self.y = y

    def multiply(self, other):
        self.x *= other.x
        self.y *= other.y

    def magnitude(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def normalize(self):
        cloned = self.clone()
        magnitude = cloned.magnitude()
        if magnitude > 1e-6:
            cloned.x /= magnitude
            cloned.y /= magnitude
        return cloned

    def lerp(self, other, t):
        self.x = self.x + t * (other.x - self.x)
        self.y = self.y + t * (other.y - self.y)

    def clone(self):
        return Vec2d(self.x, self.y)



class Block:
    def __init__(self, pos : Vec2d, id : int):
        self.pos = pos
        self.id = id

class Player:
    def __init__(self, pos : Vec2d, velocity : Vec2d):
        self.pos = pos
        self.velocity = velocity
        self.onGround = False
        self.onIce = False
        self.wasOnGround = False
        self.landed = False
        self.shootDelay = 0

    def colliding(self, block : Block):
        minX = self.pos.x + 487.5
        minY = (windowSize[0] / 2) + (self.pos.y + 13)

        maxX = (self.pos.x + blockSize) + 487.5
        maxY = (windowSize[0] / 2) + (self.pos.y + 13 + 50)

        minX2 = block.pos.x
        minY2 = windowSize[0] - block.pos.y

        maxX2 = block.pos.x + blockSize
        maxY2 = windowSize[0] - (block.pos.y + blockSize)
        if minX <= maxX2 and maxX >= minX2 and block.id != 0 and block.id != 8 and not (block.id == 9 and  mapData[int(block.pos.y/50)][int(block.pos.x/50)] > 2) and block.id != 10 and block.id != 11:
            if minY <= maxY2 and maxY >= minY2 - 100:
                return True

        return False

    def tick(self, blocks):
        global level
        global levelId
        global won
        global mapArray
        global winTime
        global mapData
        global levelPause

        keys = pygame.key.get_pressed()

        if levelPause > 0:
            levelPause -= 1
            if levelPause == 0:
                levelId = levelId + 1
                if level.isLevel(levelId):
                    loadLevel(levelId)
                else:
                    loadLevel(69420)
                    won = True
                    winTime = time.time() - startTime
                player.landed = False
                self.pos = Vec2d(-450,800)

        if not self.onGround:
            self.velocity.withY((self.velocity.y + 0.35) * 0.98)
        else:
            self.velocity.withY(0)

        if keys[pygame.K_d] and self.landed and levelPause == 0:
            if self.onGround:
                self.velocity.withX(self.velocity.x + 0.6)
            else:
                self.velocity.withX(self.velocity.x + 0.3)
        if keys[pygame.K_a] and self.landed and levelPause == 0:
            if self.onGround:
                self.velocity.withX(self.velocity.x - 0.6)
            else:
                self.velocity.withX(self.velocity.x - 0.3)

        if self.onIce:
            self.velocity.withX(self.velocity.x * 1.1)
        elif self.onGround:
            self.velocity.withX(self.velocity.x * 0.9)
        else:
            self.velocity.withX(self.velocity.x * 0.95)


        if self.onGround and (keys[pygame.K_w] or keys[pygame.K_SPACE]):
            self.velocity.withY(-8)

        self.pos.add(Vec2d(self.velocity.x, 0))
        collided = False
        for y in range(len(blocks)):
            for x in range(len(blocks[y])):
                if self.colliding(blocks[y][x]):
                    if blocks[y][x].id == 4:
                        continue
                    self.pos.subtract(Vec2d(self.velocity.x, 0))
                    self.velocity.withX(0)
                    collided = True
                    break
            if collided:
                break

        self.pos.subtract(Vec2d(0, self.velocity.y))
        self.wasOnGround = self.onGround
        self.onGround = False
        self.onIce = False
        floating = False
        collided = False

        for y in range(len(blocks)):
            for x in range(len(blocks[y])):
                if self.colliding(blocks[y][x]):
                    # print(x,y)
                    if blocks[y][x].id == 4:
                        floating = True
                        continue

                    if blocks[y][x].id == 5:
                        self.onIce = True
                    if blocks[y][x].id == 9:
                        mapData[y][x] += 1

                    if blocks[y][x].id == 6:
                        self.pos = Vec2d(-700, -150)
                        self.velocity = Vec2d(17, 0)
                        collided = True
                        self.landed = False
                        loadLevel(levelId)
                        break

                    if self.velocity.y < 0:
                        self.velocity.withY(abs(self.velocity.y))
                    else:
                        self.onGround = True
                        self.landed = True
                        self.pos.withY(windowSize[1] - ((y + 7.25) * 50))

                    collided = True

                    if blocks[y][x].id == 3:

                        levelPause = 80
                        self.velocity = Vec2d(40, 0)
                    break
            if collided:
                break

        if floating:
            if self.velocity.y < 0:
                self.velocity.withY(self.velocity.y * 1.025)
            else:
                self.velocity.withY(self.velocity.y * 0.8)


        if self.pos.y < -1000 and levelPause == 0:
            self.pos = Vec2d(-400,1000)
            self.velocity.withX(0)
            self.landed = False
            loadLevel(levelId)

class Bullet:
    def __init__(self, pos : Vec2d, dir: Vec2d, attacksPlayer : bool, image):
        self.pos = pos
        self.dir = dir
        self.attacksPlayer = attacksPlayer
        self.dir.multiply(Vec2d(10,10))
        self.image = image

    def tick(self):
        self.pos.add(self.dir)
bullets = []
player = Player(Vec2d(-400,100), Vec2d(0,0))
font = pygame.font.Font("assets/productsans.ttf", 32)
font2 = pygame.font.Font("assets/ddlc.ttf", 32)
font3 = pygame.font.Font("assets/pixel.ttf", 32)

mapArray = []
mapData = []
leaf = []
pygame.mixer.music.load("./assets/mix.wav")
pygame.mixer.music.play(-1)

def leaves():
    leaf.clear()
    for i in range(100):
        leaf.append(Leaf(Vec2d(random.randint(0, 1500), -random.randint(0, 1000)), 200, leaficos[random.randint(0,2)]))

def loadLevel(levelNum):
    global mapArray
    global mapData
    mapArray = level.readLevel(levelNum)
    bullets.clear()
    mapData = []
    leaves()
    for y in range(len(mapArray)):
        mapData.append([])
        for x in range(len(mapArray[y])):
            mapData[y].append(0)

class Leaf:
    def __init__(self, pos, lifetime, ico):
        self.pos = pos
        self.lifetime = lifetime
        self.leaf = ico

# loadLevel(levelId) will be called *after* splash_screen(), based on selected level
tB = pygame.Surface(windowSize)
tB.set_alpha(128)
tB.fill((255,229,243))
isALooser = False

def main():
    global mapData, gun, clockico, startTime
    startTime = time.time()
    loadLevel(levelId)
    clock = pygame.time.Clock()
    isRunning = True





    while isRunning:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                isRunning = False
                break
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and won:
                    dx = pygame.mouse.get_pos()[0] - 487.5
                    dy = pygame.mouse.get_pos()[1] - 387.5
                    if abs(dx) + abs(dy) < 200:
                        isRunning = False
                        pygame.quit()
                        quit(69420)

        window.blit(backgroundico,(0,0))
        # window.fill("light blue")
        blockList = []

        if player.landed:

            for ileaf in range(len(leaf)):
                oleaf = leaf[ileaf]
                oleaf.lifetime -= 1
                if oleaf.pos.x < player.pos.x - 500 or (oleaf.pos.y > (windowSize[1]/2) - player.pos.y + 400):
                    leaf[ileaf] = Leaf(Vec2d(player.pos.x + random.randint(0, 1800), -random.randint(0, 50)), 200, oleaf.leaf)

                oleaf.pos.subtract(Vec2d(random.randint(0, 5), -random.randint(3, 5)))
                window.blit(oleaf.leaf, (oleaf.pos.x - player.pos.x, oleaf.pos.y + player.pos.y))

        for y in range(len(mapArray)):
            blockList.append([])
            for x in range(len(mapArray[y])):
                blockList[y].append(Block(Vec2d(x * 50, y * 50), int(mapArray[y][x])))
                material = level.blockIndex[int(mapArray[y][x])]
                if int(mapArray[y][x]) == 6:
                    mapData[y][x] += 1
                    if mapData[y][x] > 45:
                        mapData[y][x]  = 0
                    elif mapData[y][x] > 30:
                        material = level.lava_c
                    elif mapData[y][x] > 15:
                        material = level.lava_b
                if int(mapArray[y][x]) == 10:
                    mapData[y][x]+=1
                    if mapData[y][x] > 30:
                        mapData[y][x] = 0
                    elif mapData[y][x] > 20:
                        material = level.grass_c
                    elif mapData[y][x]  > 10:
                        material = level.grass_b

                if int(mapArray[y][x]) == 9:
                    if mapData[y][x] > 2:
                        continue
                if int(mapArray[y][x]) == 0:
                    continue
                if int(mapArray[y][x]) == 8:
                    if mapData[y][x] < -100:
                        mapData[y][x] = -30
                    if mapData[y][x] < -1:
                        material = "white"
                    elif mapData[y][x] < 0:
                        continue
                    elif mapData[y][x] > 14 + random.randint(-2,2):
                        mapData[y][x] = 0
                        cloned = player.pos.clone()
                        cloned.withY((windowSize[1]/2) - player.pos.y)
                        cloned.withX(cloned.x + (windowSize[0]/2))
                        cloned.subtract(Vec2d((x + 0.5) * 50, (y + 0.5) * 50))
                        normal = cloned.normalize()

                        bullets.append(Bullet(Vec2d((x + 0.5) * 50, (y + 0.5) * 50),normal,True,bulletico))
                    mapData[y][x] += 1


                if type(material) == str:
                    pygame.draw.rect(window,material, pygame.Rect(((x * blockSize) - player.pos.x, (y * blockSize) + player.pos.y), (blockSize, blockSize)))


                else:
                    window.blit(material, ((x * blockSize) - player.pos.x, (y * blockSize) + player.pos.y))




        for bullet in bullets:
            bullet.tick()

            if bullet.pos.distance(Vec2d(player.pos.x + (windowSize[0]/2),(windowSize[1]/2) - player.pos.y)) < 25 and bullet.attacksPlayer:
                player.pos = Vec2d(-700, -150)
                player.velocity = Vec2d(17, 0)
                loadLevel(levelId)
            elif bullet.pos.x < -1000 or bullet.pos.x > 2000 or bullet.pos.y > 1000 or bullet.pos.y < -1000:
                bullets.remove(bullet)
            else:
                crashed = False
                for y in range(len(blockList)):
                    for x in range(len(blockList[y])):
                        ppos = blockList[y][x].pos.clone()
                        ppos.add(Vec2d(25,25))
                        if ppos.distance(bullet.pos) < 25 and blockList[y][x].id != 0 and blockList[y][x].id != 10 and blockList[y][x].id != 11:
                            if blockList[y][x].id == 8:
                                if bullet.attacksPlayer or  mapData[y][x] < 0:
                                    continue
                                else:
                                    mapData[y][x] = -999
                            bullets.remove(bullet)
                            crashed = True
                            break
                    if crashed:
                        break
                if not crashed:
                    window.blit(bullet.image,(bullet.pos.x - player.pos.x - 25, bullet.pos.y + player.pos.y - 25))
                    # pygame.draw.circle(window, "white", (bullet.pos.x - player.pos.x, bullet.pos.y + player.pos.y), 5)



        window.blit(character,(487.5,387.5))
        dx = pygame.mouse.get_pos()[0] - 487.5
        dy = pygame.mouse.get_pos()[1] - 387.5
        degree = (math.atan2(dx,dy) * (180/math.pi) - 90) % 360
        if degree < 0:
            degree = 360 + degree
            degree %= 360
        if dx < 0:
            gun = pygame.transform.rotate(pygame.transform.flip(pygame.transform.scale(pygame.image.load("assets/gun.png"), (50, 50)), 0, 1), degree)
        else:
            gun = pygame.transform.rotate(pygame.transform.scale(pygame.image.load("assets/gun.png"), (50, 50)), degree)

        if player.shootDelay > 0:
            player.shootDelay -= 1
        elif pygame.mouse.get_pressed()[0]:
            player.shootDelay = 10
            bulletPos = player.pos.clone()
            bulletPos.withY((windowSize[1]/2) - bulletPos.y)
            bulletPos.withX((windowSize[0]/2) + bulletPos.x)


            if dx < 0:
                bullets.append(Bullet(bulletPos, Vec2d(dx, dy).normalize(), False, bulletico2))

            else:            bullets.append(Bullet(bulletPos,Vec2d(dx,dy).normalize(),False,bulletico3))
        if won:
            window.blit(tB, (0, 0))

            if isALooser:
                window.blit(loosercrown, (385, 120))

            elif winTime < 120:
                window.blit(crown, (385, 120))
            elif winTime < 240:
                window.blit(crown2, (385, 120))
            else:
                window.blit(loosercrown, (385, 120))

            pygame.draw.rect(window, (255, 189, 224), pygame.Rect((300, 300), (400, 200)))
            pygame.draw.rect(window, (255, 229, 243), pygame.Rect((305, 305), (390, 190)))
            window.blit(font2.render("You Won! | " + str(datetime.timedelta(seconds=round(winTime))), True, "pink"),
                        (350, 350))
            window.blit(textoutline.render("Click To Exit", font2, pygame.Color(255, 255, 255),
                                           ocolor=pygame.Color(186, 85, 152)), (400, 410))

        else:
            window.blit(clockico, (15, 55))
            window.blit(font3.render("Level " + str(levelId) + " | " + level.levelNames[levelId - 1], True, "pink"), (15, 15))
            window.blit(font3.render(str(datetime.timedelta(seconds=round(time.time() - startTime))), True, "pink"), (85, 67))

        player.tick(blockList)
        pygame.display.update()

    pygame.quit()
    sys.exit(69420)

def splash_screen():
    global levelId
    global isALooser
    splash_running = True
    in_credits = False
    in_assets = False
    in_level_select = False

    font_big = pygame.font.Font("assets/ddlc.ttf", 32)
    font_small = pygame.font.Font("assets/pixel.ttf", 24)

    while splash_running:
        window.fill((255, 229, 243))  # light pink
        window.blit(chibi_monika, (30, windowSize[1] - 194 - 30))
        window.blit(chibi_yuri, (windowSize[0] - 150 - 30, windowSize[1] - 194 - 30))

        mouse_pos = pygame.mouse.get_pos()
        level_buttons = []  # ← needs to be global to check mouse input outside the draw

        if in_level_select:
            title = font_big.render("Choose a Level", True, (0, 0, 0))
            window.blit(title, title.get_rect(center=(windowSize[0] // 2, 60)))

            for i in range(1, len(level.levelNames) + 1):
                level_button = pygame.Rect(windowSize[0] // 2 - 60, 100 + i * 60, 120, 40)
                level_buttons.append((i, level_button))
                pygame.draw.rect(window, (240, 200, 255), level_button)
                label = font_small.render(f"Level {i}", True, (0, 0, 0))
                window.blit(label, label.get_rect(center=level_button.center))

            back_rect = pygame.Rect(windowSize[0] // 2 - 60, windowSize[1] - 100, 120, 40)
            pygame.draw.rect(window, (255, 192, 203), back_rect)
            window.blit(font_small.render("Back", True, (0, 0, 0)), back_rect.move(35, 10))

        elif in_credits:
            credits_lines = [
                "Created by: Hunter O.",
                "Powered by: Python and Pygame.",
                "A ton of the code is from Jason with some big",
                "and small changes, Thank you Jason for all the help :)",
                "And a little bit of help from ChatGPT.",
            ]
            credits_title = font_small.render("Credits:", True, (0, 0, 0))
            credits_title_rect = credits_title.get_rect(center=(windowSize[0] // 2, 50))
            window.blit(credits_title, credits_title_rect)
            for i, line in enumerate(credits_lines):
                text = font_small.render(line, True, (0, 0, 0))
                window.blit(text, (windowSize[0] // 2 - text.get_width() // 2, 80 + i * 30))

            back_rect = pygame.Rect(windowSize[0] // 2 - 60, windowSize[1] - 100, 120, 40)
            assets_rect = pygame.Rect(windowSize[0] // 2 - 75, windowSize[1] - 160, 230, 40)
            pygame.draw.rect(window, (255, 192, 203), back_rect)
            pygame.draw.rect(window, (200, 200, 255), assets_rect)
            window.blit(font_small.render("Back", True, (0, 0, 0)), back_rect.move(35, 10))
            assets_text = font_small.render("Assets Used", True, (0, 0, 0))
            window.blit(assets_text, assets_text.get_rect(center=assets_rect.center))

        elif in_assets:
            asset_lines = [
                "Chibi Monika: DDLC",
                "Chibi Yuri: DDLC",
                "Soundtrack: Sayo-Nara-DDLC",
                "Floating block by Me",
                "Font-1: DDLC.ttf made by Dejavu Sans",
                "Font-2: Pixel.ttf by GGBot",
                "All other assets: Jason, thank you!",
            ]
            title = font_small.render("Assets Used:", True, (0, 0, 0))
            window.blit(title, title.get_rect(center=(windowSize[0] // 2, 50)))

            for i, line in enumerate(asset_lines):
                text = font_small.render(line, True, (0, 0, 0))
                window.blit(text, text.get_rect(center=(windowSize[0] // 2, 100 + i * 30)))

            back_rect = pygame.Rect(windowSize[0] // 2 - 60, windowSize[1] - 100, 120, 40)
            pygame.draw.rect(window, (255, 192, 203), back_rect)
            window.blit(font_small.render("Back", True, (0, 0, 0)), back_rect.move(35, 10))

        else:
            # Main menu
            title = font_big.render("Warning: This game is rage inducing. Continue?", True, (255, 105, 180))
            window.blit(title, title.get_rect(center=(windowSize[0] // 2, windowSize[1] // 3)))

            yes_rect = pygame.Rect(windowSize[0] // 2 - 150, windowSize[1] // 2, 120, 50)
            no_rect = pygame.Rect(windowSize[0] // 2 + 30, windowSize[1] // 2, 370, 50)
            credits_rect = pygame.Rect(windowSize[0] // 2 - 60, windowSize[1] // 2 + 80, 140, 40)
            level_select_rect = pygame.Rect(windowSize[0] // 2 - 110, windowSize[1] // 2 + 140, 220, 40)

            pygame.draw.rect(window, (144, 238, 144), yes_rect)
            pygame.draw.rect(window, (255, 160, 122), no_rect)
            pygame.draw.rect(window, (200, 200, 255), credits_rect)
            pygame.draw.rect(window, (180, 180, 255), level_select_rect)

            window.blit(font_small.render("Yup", True, (0, 0, 0)), yes_rect.move(35, 15))
            window.blit(font_small.render("LET ME OUT OF HERE", True, (139, 0, 0)), no_rect.move(30, 15))
            window.blit(font_small.render("Credits?", True, (0, 0, 0)), credits_rect.move(20, 10))
            window.blit(font_small.render("Level Select...", True, (139, 0, 0)), level_select_rect.move(10, 10))

        # mouse stuff

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not in_credits and not in_assets and not in_level_select:
                    if yes_rect.collidepoint(mouse_pos):
                        splash_running = False
                    elif no_rect.collidepoint(mouse_pos):
                        pygame.quit()
                        sys.exit()
                    elif credits_rect.collidepoint(mouse_pos):
                        in_credits = True
                    elif level_select_rect.collidepoint(mouse_pos):
                        in_level_select = True

                elif in_level_select:
                    for lvl, rect in level_buttons:
                        if rect.collidepoint(mouse_pos):

                            levelId = lvl
                            if levelId > 1:
                                isALooser = True
                            splash_running = False
                    if back_rect.collidepoint(mouse_pos):
                        in_level_select = False
                elif in_credits:
                    if back_rect.collidepoint(mouse_pos):
                        in_credits = False
                    elif assets_rect.collidepoint(mouse_pos):
                        in_credits = False
                        in_assets = True

                elif in_assets:
                    if back_rect.collidepoint(mouse_pos):
                        in_assets = False
                        in_credits = True

                elif in_level_select:
                    for level_number, button_rect in level_buttons:
                        if button_rect.collidepoint(mouse_pos):
                            levelId = level_number
                            if levelId > 1:
                                isALooser = True
                            splash_running = False
                    if back_rect.collidepoint(mouse_pos):
                        in_level_select = False


        pygame.display.update()



if __name__ == "__main__":
    splash_screen()
    main()
