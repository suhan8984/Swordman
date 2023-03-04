import pygame
import numpy as np
from pygame.transform import rotozoom, flip
from tool import get_img, form

# initialize
size = width, height = 1425, 513
win = pygame.display.set_mode(size)
bg = rotozoom(pygame.image.load('./background.png').convert(), 0, 1)
win.fill((255, 255, 255))
win.blit(bg, (0, 0))
pygame.display.update()

pygame.mixer.init(buffer=128)
pygame.init()
clock = pygame.time.Clock()

# Load images
lGuard = get_img('Guard', num=(30, 30))
rGuard = get_img('Guard', num=(30, 30), isflip=True)

WalkLeft = get_img('walk', num=(15, 22), ang=-1)
WalkRight = get_img('walk', num=(15, 22), ang=1, isflip=True)
IdleLeft = get_img('Idle', num=(3, 3))
IdleRight = get_img('Idle', num=(3, 3), isflip=True)

JumpLeft = get_img('Jump', num=(100, 105))
JumpRight = get_img('Jump', num=(100, 105), isflip=True)

SlashLeft = get_img('slash', num=(4, 14))
del SlashLeft[6]
del SlashLeft[5]
SlashRight = get_img('slash', num=(4, 14), isflip=True)
del SlashRight[6]
del SlashRight[5]

SmashLeft = get_img('smash', num=(33, 39))
SmashRight = get_img('smash', num=(33, 39), isflip=True)
StingLeft = get_img('sting', num=(40, 46))
StingRight = get_img('sting', num=(40, 46), isflip=True)
UpperLeft = get_img('upper', num=(47, 54))
UpperRight = get_img('upper', num=(47, 54), isflip=True)
LStrongslash = get_img('Strongslash', num=(60, 66))
RStrongslash = get_img('Strongslash', num=(60, 66), isflip=True)

# idle run jump, guard, ***

vel = 6  # running velocity of swordman
x, y = 50, 205
head = 'Right'
# dy = [-20, -70, -130, -130, -70, -20]
dy = [-20, -50, -60, +60, +50, +20]
skillList = ['idle', 'walk', 'jump', 'guard', 'slash', 'smash', 'sting', 'upper', 'strongslash']
maxFrame  = [  1,      8,     6,       1,      9,        7,       7,        8,       7]
durFrame  = [  3,      4,     6,    None,      2,        3,       4,        5,       5]
countList = [  0,      0,     0,    None,      0,        0,       0,        0,       0]
adx       = [  0,      0,     0,       0,      0,        0,       0,        0,       0]
ady       = [  0,      0,     0,       0,      0,        0,       0,        0,       0]
skillState = [True, False, False,  False,  False,    False,   False,    False,   False]
skillKey = [None, None, pygame.K_SPACE, pygame.K_UP, pygame.K_a, pygame.K_f, pygame.K_s, pygame.K_w, pygame.K_d]
skillNum = len(skillList)

skillMotion = [[IdleRight, IdleLeft], [WalkRight, WalkLeft],
               [JumpRight, JumpLeft], [rGuard, lGuard],
               [SlashRight, SlashLeft], [SmashRight, SmashLeft],
               [StingRight, StingLeft], [UpperRight, UpperLeft],
               [RStrongslash, LStrongslash]]

hit_delay = False

# Cannon parameter
xlist, ylist, hlist = [], [], []
speed = 7
buffer = 0


def count(str):
    return countList[id(str)]


def state(str):
    return skillState[id(str)]


def frame(str):
    return durFrame[id(str)]


def id(str, conv=None):
    if conv is not None:
        skillState[skillList.index(str)] = conv
    return skillList.index(str)

def getState(str):
    return skillState[skillList.index(str)]


def status_check():
    global skillState, countList
    global x, y, head, hit_delay

    keys = pygame.key.get_pressed()
    pressState = [keys[item] for item in skillKey if item is not None]

    # 가드 풀어
    if not pressState[id('guard')]:
        id('guard', False)

    # x축 이동
    if sum(skillState[3:]) == 0:
        if keys[pygame.K_RIGHT] and not keys[pygame.K_UP]:
            head = 'Right'
            x += vel
            x = form(x)
        elif keys[pygame.K_LEFT] and not keys[pygame.K_UP]:
            head = 'Left'
            x -= vel
            x = form(x)

    if sum(skillState[2:]) == 0:
        # 우측 이동
        if keys[pygame.K_RIGHT] and not keys[pygame.K_UP]:
            hit_delay = False
            id('idle', False)
            id('walk', True)
        # 좌측 이동
        elif keys[pygame.K_LEFT] and not keys[pygame.K_UP]:
            hit_delay = False
            id('idle', False)
            id('walk', True)
        # 완전 정지
        else:
            id('idle', True)
            id('walk', False)
            countList[id('walk')] = 0
            hit_delay = False

    # 가만히 있거나, 달리고 있거나, 스트레이트라면 다른 공격 가능
    # 단, 스트레이트 도중 달릴 수는 없음
    if state('idle') or state('walk') or state('slash'):
        for idx in range(2, skillNum):
            if pressState[idx-2]:
                skillState = [False] * skillNum
                skillState[idx] = True
                countList[id('walk')] = 0
                if not skillState[id('slash')]:
                    countList[id('slash')] = 0
                break


def finish_move():
    global hit_delay, skillState, countList

    # 프레임을 처음으로 되돌림
    for idx in range(skillNum):
        if durFrame[idx] is not None and countList[idx] >= maxFrame[idx] * durFrame[idx]:
            countList[idx] = 0
            skillState[idx] = False
            hit_delay = False

    if skillState == [False] * skillNum:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT] or keys[pygame.K_LEFT]:
            skillState[id('walk')] = True
        else:
            skillState[id('idle')] = True


def draw_character():
    global countList, y

    # 상태 체크 + 캐릭터 그리기
    if sum(skillState) > 1:
        raise AssertionError

    if state('jump') and count('jump') % frame('jump') == 0:
        y = y + dy[count('jump')//frame('jump')]

    for idx in range(skillNum):
        pos = 0 if head == 'Right' else 1
        if skillState[idx]:
            if durFrame[idx] is None:
                win.blit(skillMotion[idx][pos][0], (x+adx[idx], y+ady[idx]))
            else:
                cframe = countList[idx]//durFrame[idx]
                if ady[idx] is not None:
                    win.blit(skillMotion[idx][pos][cframe], (x+adx[idx], y+ady[idx]))
                elif state('jump'):
                    win.blit(skillMotion[idx][pos][cframe], (x+adx[idx], y+ady[idx]))
                else:
                    raise AssertionError
                countList[idx] += 1


def check_mouse():
    global x, y
    mouse = pygame.mouse.get_pos()
    font = pygame.font.Font('Noto-Black.otf', 30)
    text = font.render("mouse: ({}, {})".format(mouse[0], mouse[1]), True, (28, 28, 0))
    text2 = font.render("character: ({}, {})".format(x, y), True, (28, 28, 0))
    text3 = font.render("{:+}, {:+}".format(mouse[0]-x, mouse[1]-y), True, (28, 28, 0))
    win.blit(text, (50, 80))
    win.blit(text2, (50, 40))
    win.blit(text3, (50, 120))


def redraw():
    win.blit(bg, (0, 0))
    status_check()
    finish_move()
    draw_character()


run = True

while run:
    clock.tick(48)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    redraw()
    check_mouse()
    pygame.display.update()


pygame.quit()
