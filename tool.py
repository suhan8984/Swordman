import pygame
from pygame.transform import rotozoom, flip


def form(x):
    width = 1425
    if x > width - 250:
        return width - 250
    elif x < -30:
        return -30
    else:
        return int(x)


def get_img(des, num, ang=0, mag=0.4, isflip=False):
    loc = './swordman'
    if not isflip:
        return [rotozoom(pygame.image.load('{}/{}.png'.format(loc, idx)), ang, mag)
                for idx in range(num[0], num[1]+1)]
    else:
        return [rotozoom(flip(pygame.image.load('{}/{}.png'.format(loc, idx)), True, False), ang, mag)
                for idx in range(num[0], num[1]+1)]
