import datetime
import time
from xmlrpc.client import DateTime
import pygame
import lib.textoutline as textoutline

import math
import os
import winsound
import random

pygame.init()

pygame.display.set_caption("Yuri's Great Escape Custom Editor")
blockSize = 50

windowSize = (1000,800)
window = pygame.display.set_mode(windowSize)
import lib.ragelevel as level

class Vec2d:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def length(self):
        return abs(self.x) + abs(self.y)

    def distance(self, other):
        return (self.x - other.x) ** 2 + (self.y - other.y) ** 2

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

    def colliding(self, block : Block):
        minX = self.pos.x + 487.5
        minY = (windowSize[0] / 2) + (self.pos.y + 13)

        maxX = (self.pos.x + blockSize) + 487.5
        maxY = (windowSize[0] / 2) + (self.pos.y + 13 + 50)

        minX2 = block.pos.x
        minY2 = windowSize[0] - block.pos.y

        maxX2 = block.pos.x + blockSize
        maxY2 = windowSize[0] - (block.pos.y + blockSize)
        if minX <= maxX2 and maxX >= minX2 and block.id != 0:
            if minY <= maxY2 and maxY >= minY2 - 100:
                return True

        return False

player = Player(Vec2d(-400,-100), Vec2d(0,0))
font = pygame.font.Font("assets/productsans.ttf", 32)
mapArray = level.readLevel(1)
level.writeLevel(1, mapArray)
font2 = pygame.font.Font("assets/ddlc.ttf", 32)
tB = pygame.Surface(windowSize)
tB.set_alpha(128)
tB.fill((255,229,243))

def main():
    clock = pygame.time.Clock()
    isRunning = True
    blockNum = 0
    lastSaved = False
    levelNum = 1
    modified = False
    global mapArray

    while isRunning:
        clock.tick(60)
      

        window.fill("black")

        keys = pygame.key.get_pressed()
        if keys[pygame.K_d]:
            player.pos.add(Vec2d(5,0))
        if keys[pygame.K_a]:
            player.pos.add(Vec2d(-5,0))
        if keys[pygame.K_w]:
            player.pos.add(Vec2d(0, 5))
        if keys[pygame.K_s]:
            player.pos.add(Vec2d(0, -5))

        if keys[pygame.K_f] and not lastSaved:
            level.writeLevel(levelNum, mapArray)
            lastSaved = True
            winsound.Beep(2000 + random.randint(0,1000),100)
            modified = False

        for y in range(len(mapArray)):
            for x in range(len(mapArray[y])):
                material =level.blockIndex[int(mapArray[y][x])]
                if type(material) == str:
                    pygame.draw.rect(window, material,
                                     pygame.Rect(((x * blockSize) - player.pos.x, (y * blockSize) + player.pos.y),
                                                 (blockSize, blockSize)))
                else:
                    window.blit(material, ((x * blockSize) - player.pos.x, (y * blockSize) + player.pos.y))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                isRunning = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    blockNum -= 1
                    if blockNum < 0:
                        blockNum = len(level.blockIndex) - 1
                    if blockNum > len(level.blockIndex) - 1:
                        blockNum = 0
                if event.key == pygame.K_RIGHT:
                    blockNum += 1
                    if blockNum < 0:
                        blockNum = len(level.blockIndex) - 1
                    if blockNum > len(level.blockIndex) - 1:
                        blockNum = 0
                if event.key == pygame.K_UP:
                    if modified:
                        winsound.Beep(200, 100)
                    else:
                        levelNum += 1
                        if level.isLevel(levelNum):
                            mapArray = level.readLevel(levelNum)
                        else:
                            mapArray = level.readLevel(69420)
                if event.key == pygame.K_DOWN:
                    if modified:
                        winsound.Beep(200, 100)
                    else:
                        levelNum -= 1
                        if levelNum > 0 and level.isLevel(levelNum):
                            mapArray = level.readLevel(levelNum)
                        elif levelNum > 0:
                            mapArray = level.readLevel(69420)
                        else:
                            levelNum = 1
                            winsound.Beep(200, 100)

            if event.type == pygame.MOUSEWHEEL:
                blockNum += event.y
                if blockNum < 0:
                    blockNum = len(level.blockIndex) - 1
                if blockNum > len(level.blockIndex) - 1:
                    blockNum = 0
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if lastSaved:
                        lastSaved = False
                    else:
                        modified = True
                        spot = Vec2d(math.floor((event.pos[0] + player.pos.x)/50),math.floor((event.pos[1] - player.pos.y)/50))
                        mapArray[min(max(spot.y,0),len(mapArray)-1)][min(max(spot.x, 0), len(mapArray[0])-1)] = blockNum
        window.blit(font.render(level.blockName[blockNum] + " | Level: " + str(levelNum), True, "white"),  (75, 12.5))

        if lastSaved:
            window.blit(tB, (0, 0))
            pygame.draw.rect(window, (255, 189, 224), pygame.Rect((300, 300), (400, 200)))
            pygame.draw.rect(window, (255, 229, 243), pygame.Rect((305, 305), (390, 190)))
            window.blit(font2.render("Saved", True, "black"),
                        (450, 350))
            window.blit(textoutline.render("Ok", font2, pygame.Color(255, 255, 255),
                                           ocolor=pygame.Color(186, 85, 152)), (475, 410))


        pygame.draw.rect(window, "white", pygame.Rect((0, 0), (60, 60)))
        mat = level.blockIndex[blockNum]
        if type(mat) == str:
            pygame.draw.rect(window, mat,
                             pygame.Rect((5,5),
                                         (blockSize, blockSize)))
        else:
            window.blit(mat, (5,5))
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
